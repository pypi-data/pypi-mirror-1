#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements the only existing facility for accessing resources
# from Pythomnic3k application - best effort distributed transaction where
# each participating resource is accessed through a separate resource pool
# managed by its own pool of threads.
#
# Example:
#
# xa = pmnc.transaction.create()
# xa.db_resource.query("SELECT ...")
# xa.http_resource.post("/", b"foo")
# db_result, http_result = xa.execute()
#
# xa = pmnc.transaction.create()
# xa.state.set(key, value)
# xa.pmnc("somecage:retry").module.method()
# call_id = xa.execute()[1]
#
# Not all of the resources may support "true" transactions, for instance
# in the above examples, sending HTTP request is irreversible and not really
# transaction-capable. Anyway, for uniformity access to all resources is
# wrapped in a transaction, possibly meaningless, and all resources are
# encouraged to implement some degree of atomicity and durability.
#
# Even if all the participating resources are transaction capable, there is
# still a chance of group commit failure, albeit a small one. At the moment
# of commit each participating resource is represented by separate thread
# waiting for decision signal, and they are signaled to commit simultaneously.
# Provided that each individual commit operation is fast and fail-safe,
# the chance of the group commit failure is small.
#
# To reiterate: this module has nothing to do with two-phase commit and it is
# intentional. All resources should attempt to make their commit operations
# fast and fail-safe, but if commit operation fails, bad luck, end of story.
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "create", "Transaction" ]

################################################################################

import os; from os import urandom
import binascii; from binascii import b2a_hex
import threading; from threading import Event
import time; from time import time, strftime
import sys; from sys import exc_info

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import interlocked_queue; from interlocked_queue import InterlockedQueue
import pmnc.thread_pool; from pmnc.thread_pool import WorkUnitTimedOut
import pmnc.samplers; from pmnc.samplers import RateSampler

###############################################################################

def create(*, __source_module_name, **options):

    # creating an instance of transaction by calling the class
    # through pmnc allows this module to be itself reloadable

    return pmnc.transaction.Transaction(__source_module_name, **options)

###############################################################################

class Transaction:

    _transaction_rate_sampler = RateSampler(10.0)

    def __init__(self, source_module_name, **options):

        self._source_module_name, self._options = source_module_name, options

        transaction_time = strftime("%Y%m%d%H%M%S")
        random_id = b2a_hex(urandom(6)).decode("ascii").upper()
        self._xid = "XA-{0:s}-{1:s}".format(transaction_time, random_id)

        self._resources, self._results = [], InterlockedQueue()
        self._decision, self._commit = Event(), Event()

        self._transaction_rate_sampler.tick()

        pmnc.log.debug("request {0:s} creates transaction {1:s}".\
                       format(pmnc.request.unique_id, self._xid))

    # this method analyzes the raw results of the yet uncommitted individual transactions
    # and returns the adjusted results thus confirming commit or throws for rollback

    def refine(self, results):
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                e, tb = result
                if isinstance(e, Exception) and type(tb).__name__ == "traceback":
                    raise e.with_traceback(tb)
        return results

    @staticmethod
    def _resource_ttl(resource_instance) -> str:
        if resource_instance.expired:
            return "expired"
        else:
            return "expires in {0:.01f} second(s)".format(resource_instance.ttl)

    # this method is used by interface_performance.py
    # to extract the current transaction rate

    @classmethod
    def get_transaction_rate(cls):
        return cls._transaction_rate_sampler.avg

    # this method is executed in context of a worker thread from the resource thread pool,
    # it initiates the transaction, executes the workload, delivers the result to the
    # original transaction thread, waits for a decision and performs commit/rollback

    def wu_participate(self, transaction_start, i, resource_name,
                       attrs, args, kwargs, res_args, res_kwargs):
        try:

            # see whether the request by which this transaction was created
            # has expired in the meantime, and if it has, simply bail out
            # because the transaction should no longer exist

            if pmnc.request.expired:
                raise Exception("execution of resource {0:s} in transaction "
                                "{1:s} was late by {2:.01f} second(s)".\
                                format(resource_name, self._xid, pmnc.request.expired_for))

            # the pending interval is measured from the beginning of the
            # transaction, not from the beginning of the request

            pending_ms = int((time() - transaction_start) * 1000)
            pmnc.performance.sample("resource.{0:s}.pending_time".\
                                    format(resource_name), pending_ms)

            pmnc.log.debug("resource {0:s} begins to execute in transaction {1:s}, "
                           "request deadline in {2:.01f} second(s)".\
                           format(resource_name, self._xid, pmnc.request.remain))

            resource_pool, resource_instance = None, None
            try:

                transaction_began = False

                try:

                    # allocate a resource instance from a specific resource pool

                    resource_pool = pmnc.shared_pools.get_resource_pool(resource_name)
                    resource_instance = resource_pool.allocate()
                    try:

                        # see whether the resource can be used at all in
                        # as much time as the current request has left

                        remain = pmnc.request.remain
                        if remain < resource_instance.min_time:
                            raise Exception("transaction {0:s} is declined by resource {1:s} because "
                                            "request {2:s} has only {3:.01f} second(s) left to execute".\
                                            format(self._xid, resource_name, pmnc.request.unique_id, remain))

                        pmnc.log.debug("resource instance {0:s} is used in transaction "
                                       "{1:s}, {2:s}".format(resource_instance.name,  self._xid,
                                                             self._resource_ttl(resource_instance)))

                        # replay attribute accesses to obtain the actual target method

                        target_method = resource_instance
                        for attr in attrs:
                             target_method = getattr(target_method, attr)

                        # begin and execute a transaction on the resource and register its duration

                        with pmnc.performance.timing("resource.{0:s}.processing_time".format(resource_name)):
                            resource_instance.begin_transaction(self._xid,
                                                                source_module_name = self._source_module_name,
                                                                transaction_options = self._options,
                                                                resource_args = res_args,
                                                                resource_kwargs = res_kwargs)
                            transaction_began = True
                            result = target_method(*args, **kwargs)

                    except Exception as e:
                        resource_instance.expire() # if it has thrown then it is dead
                        raise
                    else:
                        resource_instance.reset_idle_timeout() # if it has returned then it is alive

                except Exception as e:
                    pmnc.log.warning("resource {0:s} failed to execute in transaction {1:s}: "
                                     "{2:s}".format(resource_name, self._xid, exc_string()))
                    result = (e, exc_info()[-1])
                    failure = True
                else:
                    failure = False

                # register the actual result of this transaction participant
                # with no respect to the distributed transaction result

                pmnc.performance.event("resource.{0:s}.transaction_rate.{1:s}".\
                                       format(resource_name, failure and "failure" or "success"))

                # deliver the intermediate result to the transaction and wait for its decision

                self._results.push((i, result))

                pmnc.log.debug("resource {0:s} is waiting for decision in transaction "
                               "{1:s}".format(resource_name, self._xid))

                if not pmnc.request.wait(self._decision):
                    pmnc.log.warning("resource {0:s} had to abandon waiting for decision in "
                                     "transaction {1:s}".format(resource_name, self._xid))
                    failure = True

                # in case a resource was not allocated from the pool at all, the result
                # has been an exception but there is nothing to commit or rollback

                if not resource_instance:
                    return "failure" # nothing to commit or rollback

                # rollback or commit and return the actual decision

                if not self._commit.is_set() or failure:
                    try:
                        if transaction_began:
                            resource_instance.rollback()
                        pmnc.log.debug("resource {0:s} rolled back in transaction {1:s}".\
                                       format(resource_name, self._xid))
                    except:
                        pmnc.log.warning("resource {0:s} failed to rollback in transaction {1:s}: "
                                         "{2:s}".format(resource_name, self._xid, exc_string()))
                        return "failure"
                    else:
                        return failure and "failure" or "rollback"
                else:
                    try:
                        assert transaction_began
                        resource_instance.commit()
                        pmnc.log.debug("resource {0:s} committed in transaction {1:s}".\
                                       format(resource_name, self._xid))
                    except:
                        pmnc.log.warning("resource {0:s} failed to commit in transaction {1:s}: "
                                         "{2:s}".format(resource_name, self._xid, exc_string()))
                        return "failure"
                    else:
                        return "commit"

            finally:
                if resource_pool and resource_instance: # release the resource instance
                    pmnc.log.debug("resource instance {0:s} is released, {1:s}".\
                                   format(resource_instance.name, self._resource_ttl(resource_instance)))
                    resource_pool.release(resource_instance)

        except:
            pmnc.log.error(exc_string()) # log and ignore

    # this method initiates transaction execution for each of the individual
    # resources each through its own thread pool, collects the intermediate
    # results of the yet uncommitted transactions and makes the commit/rollback
    # decision

    def execute(self):

        pmnc.log.info("transaction {0:s} ({1:s}) created by request {2:s} begins, deadline in {3:.01f} "
                      "second(s)".format(self._xid, ", ".join("{0:s}.{1:s}".format(t[0], ".".join(t[1]))
                                                              for t in self._resources),
                                         pmnc.request.unique_id, pmnc.request.remain))
        try:

            # initiate execution of all the individual resources each through its own thread pool

            transaction_start = time()
            work_units = []

            for i, (resource_name, attrs, args, kwargs, res_args, res_kwargs) in enumerate(self._resources):
                thread_pool = pmnc.shared_pools.get_thread_pool(resource_name)
                request = pmnc.request.clone()
                work_unit = thread_pool.enqueue(request, self.wu_participate, (transaction_start, i,
                                                resource_name, attrs, args, kwargs, res_args, res_kwargs), {})
                work_units.append(work_unit)

            # wait for all the individual resources to deliver intermediate results

            results = []
            while len(results) < len(self._resources):
                result = pmnc.request.pop(self._results)
                if result is None:
                    raise Exception("request deadline waiting for intermediate results")
                results.append(result)

            # perform result interpretation and possibly post-processing,
            # the refine method throws to initiate rollback

            results = self.refine(tuple(result for i, result in sorted(results)))

        except:
            pmnc.log.warning("transaction {0:s} is being rolled back: {1:s}".\
                             format(self._xid, exc_string()))
            raise
        else:
            pmnc.log.debug("transaction {0:s} is being committed".format(self._xid))
            self._commit.set()
        finally:
            self._decision.set()

        # wait for all the individual resources to commit, in no particular order

        for i, work_unit in enumerate(work_units):
            resource_name = self._resources[i][0]
            try:
                resource_decision = work_unit.wait() # this blocks until work_unit completes or request deadline
            except WorkUnitTimedOut:
                pmnc.log.warning("transaction {0:s} had to abandon waiting for commit "
                                 "from resource {1:s}".format(self._xid, resource_name))
                raise
            if resource_decision != "commit":
                raise Exception("transaction {0:s} got an unexpected commit decision from resource "
                                "{1:s}: {2:s}".format(self._xid, resource_name, resource_decision))

        # transaction is a complete success

        pmnc.log.info("transaction {0:s} completes successfully".format(self._xid))

        return results

    # the following methods and the supporting class collect arguments for participating resources

    def __getattr__(self, resource_name):
        return Transaction.ResourceArgumentCollector(resource_name, self._collect)

    class ResourceArgumentCollector:

        def __init__(self, resource_name, collect):
            self._resource_name, self._collect = resource_name, collect
            self._attrs, self._res_args, self._res_kwargs = [], (), {}

        def __getattr__(self, name):
            self._attrs.append(name)
            return self

        def __call__(self, *args, **kwargs):
            if not self._attrs:
                self._res_args, self._res_kwargs = args, kwargs
                return self
            else:
                self._collect(self._resource_name, self._attrs, args, kwargs,
                              self._res_args, self._res_kwargs)

    def _collect(self, resource_name, attrs, args, kwargs, res_args, res_kwargs):
        self._resources.append((resource_name, attrs, args, kwargs, res_args, res_kwargs))
        pmnc.log.debug("resource {0:s} joins transaction {1:s}".\
                       format(resource_name, self._xid))

###############################################################################

def self_test():

    from pmnc.request import fake_request
    from expected import expected
    from typecheck import by_regex
    from threading import Thread
    from random import randint
    from pmnc.timeout import Timeout

    ###################################

    def test_void():
        fake_request(1.0)
        xa = pmnc.transaction.create()
        xa.execute()

    test_void()

    ###################################

    def test_rate():
        fake_request(4.0)
        t = Timeout(2.0)
        while not t.expired:
            xa = pmnc.transaction.create()
            xa.execute()
        xa = pmnc.transaction.create()
        xa.execute()
        assert xa.get_transaction_rate() > 1.0

    test_rate()

    ###################################

    def test_execute():
        fake_request(1.0)
        xa = pmnc.transaction.create(opt1 = "111", opt2 = "222")
        xa.test("foo", biz = "baz").execute(1, "2", a = "b")
        res = xa.execute()[0]
        xid = res["xid"]; assert by_regex("XA-[0-9]{14}-[0-9A-F]{12}")(xid)
        args = res["args"]; assert args == (1, "2")
        kwargs = res["kwargs"]; assert kwargs == { "a": "b" }
        resource_args = res["resource_args"]; assert resource_args == ("foo", )
        resource_kwargs = res["resource_kwargs"]; assert resource_kwargs == { "biz": "baz" }
        transaction_options = res["transaction_options"]; assert transaction_options == { "opt1": "111", "opt2": "222" }
        config = res["config"]; assert config == { "p1": "v1", "p2": "v2" } # see config_resource_test.py

    test_execute()

    ###################################

    def test_pool_exhaust():
        fake_request(3.0)
        xa = pmnc.transaction.create()
        xa.test.execute()
        xa.test.execute()
        xa.test.execute()
        xa.test.execute() # one too many, the pool has size 3, results in deadlock
        with expected(Exception("request deadline waiting for intermediate results")):
            xa.execute()

    test_pool_exhaust()

    ###################################

    def test_resource_decline():

        rq = fake_request(0.4)
        xa = pmnc.transaction.create()
        xa.test.execute()
        with expected(Exception("transaction {0:s} is declined by resource test because "
                                "request {1:s} has only ".format(xa._xid, rq.unique_id))):
            xa.execute()

    test_resource_decline()

    ###################################

    def test_fail_execute():
        fake_request(1.0)
        xa = pmnc.transaction.create(fail_execute = "error message")
        xa.test.execute()
        with expected(Exception("error message")):
            xa.execute()

    test_fail_execute()

    ###################################

    def test_delay_execute():
        fake_request(1.0)
        xa = pmnc.transaction.create(delay_execute = 2.0)
        xa.test.execute()
        with expected(Exception("request deadline waiting for intermediate results")):
            xa.execute()

    test_delay_execute()

    ###################################

    def test_fail_commit():
        fake_request(1.0)
        xa = pmnc.transaction.create(fail_commit = "error message")
        xa.test.execute()
        with expected(Exception("transaction {0:s} got an unexpected commit decision "
                                "from resource test: failure".format(xa._xid))):
            xa.execute()

    test_fail_commit()

    ###################################

    def test_delay_commit():
        fake_request(1.0)
        xa = pmnc.transaction.create(delay_commit = 2.0)
        xa.test.execute()
        with expected(WorkUnitTimedOut):
            xa.execute()

    test_delay_commit()

    ###################################

    def test_fail_rollback():
        fake_request(1.0)
        xa = pmnc.transaction.create(fail_execute = "failure", fail_rollback = "error message")
        xa.test.execute()
        with expected(Exception("failure")):
            xa.execute()

    test_fail_rollback()

    ###################################

    def test_delay_rollback():
        fake_request(1.0)
        xa = pmnc.transaction.create(fail_execute = "failure", delay_rollback = 2.0)
        xa.test.execute()
        with expected(Exception("failure")):
            xa.execute()

    test_delay_rollback()

    ###################################

    def test_perf():

        N = 256

        def threads(n, f):
            ths = [ Thread(target = f, args = (N // n, )) for i in range(n) ]
            start = time()
            for th in ths: th.start()
            for th in ths: th.join()
            return int(N  / (time() - start))

        def test_transaction(n):
            for i in range(n):
                fake_request(10.0)
                xa = pmnc.transaction.create()
                xa.test.execute()
                xa.execute()

        def state_transaction(n):
            for i in range(n):
                fake_request(30.0)
                xa = pmnc.transaction.create()
                xa.state.set(str(randint(0, 1000000)), i)
                xa.execute()

        pmnc.log("begin performance test (may take a few minutes)")
        pmnc._loader._set_log_priority(4)

        test_1 = threads(1, test_transaction)
        test_4 = threads(4, test_transaction)
        test_16 = threads(16, test_transaction)
        test_64 = threads(64, test_transaction)

        pmnc.log("{0:d}/{1:d}/{2:d}/{3:d} empty transaction(s) per second".\
                 format(test_1, test_4, test_16, test_64))

        state_1 = threads(1, state_transaction)
        state_4 = threads(4, state_transaction)
        state_16 = threads(16, state_transaction)
        state_64 = threads(64, state_transaction)

        pmnc.log("{0:d}/{1:d}/{2:d}/{3:d} state transaction(s) per second".\
                 format(state_1, state_4, state_16, state_64))

        pmnc._loader._set_log_priority(6)

        pmnc.log("end performance test")

    test_perf()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF