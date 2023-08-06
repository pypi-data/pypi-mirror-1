#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements the retried call facility -
# asynchronous RPC with reliable messaging semantics.
#
# Application code initiates a retried call using
#
# retry_id = pmnc("target_cage:retry").module.method() # to call other cage
# retry_id = pmnc(":retry").module.method() # to call this cage
#
# or in transactions with other resources
#
# xa = pmnc.transaction.create()
# xa.pmnc("target_cage:retry").module.method()
# xa.jms.send("message text", JMSCorrelationID = "foo")
# retry_id, jms_message_id = xa.execute()
#
# such calls put the call information to persistent storage and return
# immediately with some globally unique random id for the new call.
# Later on attempts to execute the target method are performed.
#
# Each attempt to execute the target method is done in TPM-like manner:
#
# 1. A message with a wrapped call in it is loaded from the persistent state
#    in a transaction, and the transaction stays uncommitted.
# 2. An attempt to execute the target method is performed.
# 3. If it returns successfully, the transaction is committed and that's it.
# 4. If it throws any exception, the transaction is rolled back, the message
#    remains on storage and its execution will be retried after a while.
#
# Notes:
#
# 1. Attempts are infinite, the called method must occassionally succeed
#    or it will be retried forever.
#
# *) The calling code can optionally specify absolute expiration time
#    after which the call will be dropped and no longer retried:
#    pmnc(":retry", expires_in = 3600.0).module.method()
#
# 2. For a retried call to another cage, there is an additional step (also
#    retried infinitely) - transmission of the call to the target cage.
#    When the message containing the call is delivered to the target cage,
#    it is immediately put to persistent storage there and from that moment
#    on to retry the call locally is entirely the responsibility of the
#    target cage.
#
# 3. The calling code can specify a unique id of its own, to prevent
#    duplicate execution, for example
#    retry_id1 = pmnc(":retry", id = "transfer/123").module.method()
#    retry_id2 = pmnc(":retry", id = "transfer/123").module.method()
#    then retry_id1 and retry_id2 are different but only one of them
#    will be actually executed.
#
# 4. Retried calls have *no* FIFO semantics, they can arrive in any
#    order, especially after (independent) retry attempts.
#
# Design goals:
#
# 1. To minimize the chance of failure as much as possible. A message
#    cannot be lost, but it can (if power is cut at the right moment)
#    be duplicated. The chances of this are very small but the methods
#    that are to be called in retried way should better be prepared.
#    For example, a target method can be something like this:
#
#    def method(): # in module.py
#        retry_ctx = pmnc.request.parameters["retry"]
#        retry_id = retry_ctx["id"]
#        attempt = retry_ctx["attempt"]
#        start = retry_ctx["start"]
#        if attempt > 10 or time() > start + 3600:
#            return # do nothing, too late or too many attempts
#        try:
#            ... insert into db (primary_key) values (retry_id) ...
#        except PrimaryKeyViolation:
#            pass # ok, duplicate attempt
#
# 2. To allow the retried calls to accumulate when a cage receives
#    more incoming calls that it can process at the moment, but at
#    the same time to prevent it from becoming overwhelmed with
#    retry attempts. This way retried calls facility can be used
#    as a buffer to handle load peaks or temporary outages that would
#    otherwise have resulted in request failures visible to the clients.
#
# Sample retry interface configuration (config_interface_retry.py):
#
# config = dict \
# (
# protocol = "retry",        # meta
# queue_count = 4,           # maximum number of retried calls scheduled concurrently
# retry_interval = 600.0,    # seconds between attempts to execute retried calls
# retention_time = 259200.0, # seconds to keep history of successfully executed calls
# )                          # (once a call gets older than that, it can be duplicated)
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource", "self_test_loopback", "self_test_retried" ]

###############################################################################

import pickle; from pickle import dumps as pickle, loads as unpickle
import threading; from threading import current_thread, Lock, Event
import os; from os import urandom
import binascii; from binascii import b2a_hex
import time; from time import time, strftime

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck, optional, by_regex
import interlocked_queue; from interlocked_queue import InterlockedQueue
import interlocked_counter; from interlocked_counter import InterlockedCounter
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource
import pmnc.timeout; from pmnc.timeout import Timeout
import pmnc.threads; from pmnc.threads import HeavyThread
import pmnc.work_sources; from pmnc.work_sources import WorkSources

###############################################################################
# the following class combines blazingly fast persistent queue
# for small items with slower database option for big ones

class PersistentQueue:

    _q_opts = dict(pagesize = 32768, re_pad = 0x00, q_extentsize = 64)
    _db_opts = dict(pagesize = 32768)

    @typecheck
    def __init__(self, name: str, re_len: int):
        self._re_len = re_len
        self._queue = pmnc.state.get_queue(name, re_len = re_len, **self._q_opts)
        self._off_db = pmnc.state.get_database(name, **self._db_opts)

    def push(self, txn, value):
        stored_value = pickle(value)
        if len(stored_value) <= self._re_len:
            self._queue.append(stored_value, txn)
        else:
            off_key = b2a_hex(urandom(15))
            self._queue.append(b"." + off_key, txn)
            self._off_db.put(off_key, stored_value, txn)

    def pop(self, txn):
        queue_item = self._queue.consume(txn)
        if queue_item is not None:
            stored_value = queue_item[1]
            if stored_value.startswith(b"."):
                off_key = stored_value[1:31]
                stored_value = self._off_db.get(off_key, None, txn)
                self._off_db.delete(off_key, txn)
            return unpickle(stored_value)

    def peek(self, txn):
        crs = self._queue.cursor(txn)
        try:
            queue_item = crs.first()
            if queue_item is not None:
                stored_value = queue_item[1]
                if stored_value.startswith(b"."):
                    off_key = stored_value[1:31]
                    stored_value = self._off_db.get(off_key, None, txn)
                return unpickle(stored_value)
        finally:
            crs.close()

###############################################################################

class PersistentSet:

    _db_opts = dict(pagesize = 32768)

    @typecheck
    def __init__(self, name: str):
        self._db = pmnc.state.get_database(name, **self._db_opts)

    def add_new(self, txn, key):
        key = pickle(key)
        if self._db.get(key, None, txn) is None:
            self._db.put(key, None, txn)
            return True
        else:
            return False

    def remove(self, txn, key):
        self._db.delete(pickle(key), txn)

###############################################################################
# this utility class is used to keep track of messages that failed
# to move to the slow queue at rollback

class InterlockedSet:

    def __init__(self):
        self._lock, self._set = Lock(), set()

    def add(self, id):
        with self._lock:
            self._set.add(id)

    def remove(self, id):
        with self._lock:
            self._set.remove(id)

    def __contains__(self, id):
        with self._lock:
            return id in self._set

###############################################################################

class Interface:

    @typecheck
    def __init__(self, name: str, *,
                 queue_count: int,
                 retry_interval: float,
                 retention_time: float):

        self._name = name
        self._retry_interval = retry_interval
        self._retention_time = retention_time

        # allocate private persistent queues and databases

        # raw queue contains whole messages that have just been
        # pushed but not yet filtered and accepted for execution

        self._raw_queue = PersistentQueue("raw", self._large_queue_re_len)

        # fast queues contain whole messages that have been
        # filtered and accepted for execution

        self._fast_queues = \
            tuple(PersistentQueue("fast_{0:02d}".format(i), self._large_queue_re_len)
                  for i in range(queue_count))

        # slow queue contains whole messages that are waiting for retry

        self._slow_queue = PersistentQueue("slow", self._large_queue_re_len)

        # done queues contain just ids of messages executed previously
        # and therefore have smaller space-saving records

        self._done_queues = \
            tuple(PersistentQueue("done_{0:02d}".format(i), self._small_queue_re_len)
                  for i in range(queue_count))

        # filter database contains ids of messages that have
        # already been accepted for execution

        self._filter_db = PersistentSet("filter")

        # fast queues are used in round-robin fashion using this counter

        self._fast_queue_ctr = InterlockedCounter(queue_count)

        # these structures are used to notify interface threads
        # about incoming work and to limit worker thread allocation

        self._raw_work = WorkSources(1, self._work_timeout)
        self._fast_work = WorkSources(queue_count, self._work_timeout)

        # because moving messages to the slow queue to initiate retry
        # is a failure-prone operation, we keep track of messages that
        # have to go to the slow queue instead of being processed

        self._failed_messages = InterlockedSet()

    name = property(lambda self: self._name)

    ###################################
    # various tuning parameters rather unlikely to change

    _work_timeout = 30.0 # seconds between forced scan of persistent queues
    _lazy_timeout = 15.0 # seconds between reassessing messages pending for retry

    _large_queue_re_len = 3072
    _small_queue_re_len = 128

    ###################################

    def start(self):

        # raw thread moves messages from the raw queue to fast queues,
        # consults and updates the filter at the same time

        self._raw_thread = HeavyThread(target = self._raw_thread_proc,
                                       name = "{0:s}:raw".format(self._name))
        self._raw_thread.start()

        # scheduler thread picks messages from fast queues, schedules
        # them for execution and moves them to slow queue upon failure

        self._scheduler_thread = HeavyThread(target = self._scheduler_thread_proc,
                                             name = "{0:s}:sch".format(self._name))
        self._scheduler_thread.start()

    ###################################

    def cease(self):

        self._scheduler_thread.stop()
        self._raw_thread.stop()

    ###################################

    def stop(self):

        pass

    ###################################
    # the raw_thread keeps reading messages from the raw queue,
    # filtering and dispatching them to the fast queues

    def _raw_thread_proc(self):

        lazy_timeout = Timeout(self._lazy_timeout)

        while True: # lifetime loop
            try:

                thread_stopped, raw_queue_idx = \
                    self._raw_work.begin_work(self._work_timeout * 2)
                if thread_stopped:
                    break

                # the way _raw_work object works, begin_work will return in
                # _work_timeout even though there is no actual work to do,
                # therefore the code below gets executed periodically even
                # when the cage is idle

                # because the poll timeout is bigger than the queue timeout
                # the _raw_work structure will always report the only raw queue
                # as having work to do, and since it has index 0, there goes

                assert raw_queue_idx == 0

                try:

                    # pop a message from the raw queue, consult the filter
                    # to see if it is a duplicate, and if not post it
                    # to a fast queue, all in one transaction

                    filtered_id, queue_idx = \
                        pmnc.state.implicit_transaction(self._filter_raw_queue)

                    # if a message has been extracted and it wasn't a duplicate
                    # then notify the scheduler thread that one of its fast queues
                    # needs attention

                    if queue_idx is not None:
                        pmnc.log.info("retried call {0:s} has been accepted "
                                      "for execution".format(filtered_id))
                        self._fast_work.add_work(queue_idx)
                    elif filtered_id is not None:
                        pmnc.log.info("retried call {0:s} has already been accepted "
                                      "for execution".format(filtered_id))

                    # if a message has been extracted at all, duplicate or not,
                    # post work to this thread itself to repeat polling immediately

                    if filtered_id is not None:
                        self._raw_work.add_work(raw_queue_idx)

                finally:
                    self._raw_work.end_work(raw_queue_idx)

                # the following code is executed periodically and is totally
                # independent from the rest of this thread's code, it could
                # be moved to a separate thread, but let's keep the number
                # of threads down

                if lazy_timeout.expired:
                    try:
                        self._retry_calls()
                        self._clean_up_filter()
                    finally:
                        lazy_timeout.reset()

            except:
                pmnc.log.error(exc_string()) # log and ignore

    ###################################
    # the scheduler_thread keeps scheduling requests for polling
    # fast queues and processing incoming messages

    def _scheduler_thread_proc(self):

        while True: # lifetime loop
            try:

                thread_stopped, queue_idx = \
                    self._fast_work.begin_work(self._work_timeout * 2)
                if thread_stopped:
                    break

                # the way _fast_work object works, begin_work will return in
                # _work_timeout even though there is no actual work to do,
                # therefore the code below gets executed periodically even
                # when the cage is idle

                # because the poll timeout is bigger than the queue timeout
                # the _fast_work structure will always report some fast queue
                # as having work to do, therefore

                assert 0 <= queue_idx < len(self._fast_queues)

                try:
                    request_timeout = pmnc.config_interfaces.get("request_timeout")
                    request = pmnc.interfaces.begin_request(timeout = request_timeout,
                                                            interface = self._name,
                                                            protocol = "retry",
                                                            parameters = dict())
                except:
                    self._fast_work.end_work(queue_idx)
                    raise

                # note that we introduce a request without being sure that it is going
                # to actually execute anything, therefore log messages are emitted and
                # performance is updated only in wu_poll_fast_queue when we are certain
                # that the persistent queue indeed holds a message to be processed

                pmnc.log.debug("interface {0:s} introduces request {1:s} for polling "
                               "fast queue #{2:02d}, deadline in {3:.01f} second(s)".\
                               format(self._name, request.unique_id, queue_idx, request.remain))

                # the fast queue polling requests are fire-and-forget

                pmnc.interfaces.enqueue(request, self.wu_poll_fast_queue, (queue_idx, ), {})

            except:
                pmnc.log.error(exc_string()) # log and ignore

    ###################################
    # this method is periodically called by the raw thread
    # to move the head of the slow queue to the fast queues

    def _retry_calls(self):

        while not current_thread().stopped():

            filtered_id, queue_idx = \
                pmnc.state.implicit_transaction(self._pop_slow_queue)

            if filtered_id is not None and queue_idx is not None:
                pmnc.log.info("retried call {0:s} has been accepted "
                              "for retry".format(filtered_id))
                self._fast_work.add_work(queue_idx)
            else:
                break

    ###################################
    # this method moves one item from the slow queue to a fast queue

    def _pop_slow_queue(self, txn): # this method is called in transaction

        slow_queue_item = self._slow_queue.peek(txn)
        if slow_queue_item is None:
            return None, None

        # see if the head of the slow queue is old enough to be retried

        failure_timestamp, wrapped_message = slow_queue_item
        if int(time()) < failure_timestamp + self._retry_interval:
            return None, None
        assert self._slow_queue.pop(txn) == slow_queue_item

        # push the message from the slow queue to the next fast queue

        queue_idx = self._fast_queue_ctr.next()
        fast_queue = self._fast_queues[queue_idx]
        fast_queue.push(txn, wrapped_message)

        filtered_id = RetriedCallMessage.unwrap(wrapped_message).filtered_id
        return filtered_id, queue_idx

    ###################################
    # this method is periodically called by the raw thread to remove
    # expired heads of the done queues from the filter

    def _clean_up_filter(self):

        removed_records_total = 0

        while not current_thread().stopped():
            removed_records = pmnc.state.implicit_transaction(self._pop_done_queues)
            if removed_records > 0:
                removed_records_total += removed_records
            else:
                break

        if removed_records_total > 0:
            pmnc.log.debug("removed {0:d} expired filter record(s)".\
                           format(removed_records_total))

    ###################################
    # this method pops an item off each done queues and removes
    # popped message ids from the filter if they are old enough

    def _pop_done_queues(self, txn): # this method is called in transaction

        pop_count = 0

        for done_queue in self._done_queues:

            done_queue_item = done_queue.peek(txn)
            if done_queue_item is None:
                continue  # proceed to the next done queue

            # see if the head of this done queue is old enough to be dropped

            success_timestamp, filtered_id = done_queue_item
            if int(time()) < success_timestamp + self._retention_time:
                continue # proceed to the next done queue
            assert done_queue.pop(txn) == done_queue_item

            # remove the expired record from the filter

            self._filter_db.remove(txn, filtered_id)

            pop_count += 1

        return pop_count

    ###################################
    # this method is called by one of the worker threads
    # to extract and process a message from a fast queue

    def wu_poll_fast_queue(self, queue_idx):
        try:

            try:

                # see for how long the request was on the execution queue up to this moment
                # and whether it has expired in the meantime, if it did there is no reason
                # to proceed and we simply bail out

                if pmnc.request.expired:
                    raise Exception("processing of request {0:s} was late by {1:.01f} second(s)".\
                                    format(pmnc.request.unique_id, pmnc.request.expired_for))

                pending_ms = int(pmnc.request.elapsed * 1000)

                # initiate a transaction and pop a message from the fast queue

                txn, commit, rollback = pmnc.state.start_transaction(__name__)
                try:
                    txn, message = \
                        pmnc.state.explicit_transaction(__name__,
                            txn, self._pop_fast_queue_success, queue_idx)
                except:
                    rollback(txn)
                    raise

                # note that the transaction remains open

                if message is not None: # process the message and commit upon success

                    message_id = message.unique_id

                    if message_id not in self._failed_messages: # the message is to be processed

                        try:
                            # returns True if the call has been executed or False if it has been cancelled
                            success = self._process_message(message, pending_ms)
                        except:
                            error = exc_string()
                            rollback(txn) # rollback fruitful pop
                            self._failed_messages.add(message.unique_id)
                            try: # move the message to the slow queue
                                pmnc.state.implicit_transaction(
                                    self._pop_fast_queue_failure, queue_idx, message.unique_id)
                            except Exception as e:
                                pmnc.log.warning("{0:s} has failed but could not be moved to the "
                                                 "slow queue ({1:s}), will be moved later: {2:s}".\
                                                 format(message, e, error))
                                # note that message_id remains in _failed_messages
                            else:
                                self._failed_messages.remove(message_id)
                                pmnc.log.warning("{0:s} has failed and will be retried: "
                                                 "{1:s}".format(message, error))
                        else:
                            commit(txn) # commit fruitful pop
                            if success:
                                pmnc.log.info("{0:s} has succeeded".format(message))
                            else:
                                pmnc.log.info("{0:s} has been cancelled".format(message))

                    else: # the previous attempt failed but the message remained in the fast queue

                        rollback(txn) # rollback fruitful pop
                        try: # repeat attempt to move the message to the slow queue
                            pmnc.state.implicit_transaction(
                                self._pop_fast_queue_failure, queue_idx, message.unique_id)
                        except:
                            pmnc.log.warning("{0:s} has previously failed but could not be "
                                             "moved to the slow queue again: {1:s}".\
                                             format(message, exc_string()))
                            # note that message_id remains in _failed_messages
                        else:
                            self._failed_messages.remove(message_id)
                            pmnc.log.info("{0:s} has previously failed and "
                                          "will be retried".format(message))

                    self._fast_work.add_work(queue_idx) # to process this queue again immediately

                else: # the fast queue is empty

                    commit(txn) # commit empty pop

            finally:
                self._fast_work.end_work(queue_idx)

        except:
            pmnc.log.error(exc_string()) # log and ignore

        pmnc.interfaces.end_request(pmnc.request)

    ###################################
    # this method is called by a worker thread to actually execute the retried call

    def _process_message(self, message, pending_ms):

        pmnc.log.info("request {0:s} previously introduced by interface {1:s} is "
                      "{2:s} {3:s}, deadline in {4:.01f} second(s)".\
                      format(pmnc.request.unique_id, self._name,
                             message.attempt == 1 and "executing" or "retrying",
                             message, pmnc.request.remain))

        pmnc.performance.event("interface.{0:s}.request_rate".format(self._name))
        try:

            pmnc.performance.sample("interface.{0:s}.pending_time".\
                                    format(self._name), pending_ms)

            with pmnc.performance.timing("interface.{0:s}.processing_time".\
                                         format(self._name)):
                result = message.execute()

        except:
            elapsed_ms = int(pmnc.request.elapsed * 1000)
            pmnc.performance.sample("interface.{0:s}.response_time.failure".\
                                    format(self._name), elapsed_ms)
            pmnc.performance.event("interface.{0:s}.response_rate.failure".\
                                   format(self._name))
            raise
        else:
            elapsed_ms = int(pmnc.request.elapsed * 1000)
            pmnc.performance.sample("interface.{0:s}.response_time.success".\
                                    format(self._name), elapsed_ms)
            pmnc.performance.event("interface.{0:s}.response_rate.success".\
                                   format(self._name))
            return result

    ###################################

    def _filter_raw_queue(self, txn): # this method is executed within a transaction

        # pop a message from the raw queue

        wrapped_message = self._raw_queue.pop(txn)
        if wrapped_message is None:
            return None, None # the raw queue is empty
        message = RetriedCallMessage.unwrap(wrapped_message)

        # extract filtered_id from the message

        filtered_id = message.filtered_id

        # filter the message against a database of already accepted,
        # and add it to the the filter if it hasn't been there

        if self._filter_db.add_new(txn, filtered_id):

            # push the original message to the next fast queue

            queue_idx = self._fast_queue_ctr.next()
            fast_queue = self._fast_queues[queue_idx]
            fast_queue.push(txn, wrapped_message)

            return filtered_id, queue_idx # return the index of the picked queue

        else: # duplicate, ignore

            return filtered_id, None

    ###################################
    # success action is to register the time of successful completion (now)
    # by pushing filtered id of the message to the corresponding done queue

    def _pop_fast_queue_success(self, txn, queue_idx): # this method is executed within a transaction

        fast_queue = self._fast_queues[queue_idx]
        wrapped_message = fast_queue.pop(txn)
        if wrapped_message is not None:
            message = RetriedCallMessage.unwrap(wrapped_message)
            success_timestamp = int(time())
            done_queue_item = (success_timestamp, message.filtered_id)
            done_queue = self._done_queues[queue_idx]
            done_queue.push(txn, done_queue_item)
            pmnc.log.debug("moving {0:s} from fast queue #{1:02d} to done "
                           "queue #{1:02d}".format(message, queue_idx))
            return message

    ###################################
    # failure action is to update the message contents and push it
    # to the slow queue, also registering the time of failure

    def _pop_fast_queue_failure(self, txn, queue_idx, original_unique_id): # this method is executed within a transaction

        fast_queue = self._fast_queues[queue_idx]
        wrapped_message = fast_queue.pop(txn)
        if wrapped_message is not None:
            message = RetriedCallMessage.unwrap(wrapped_message)
            assert message.unique_id == original_unique_id # make sure we move the right message
            message.tick_retry()
            failure_timestamp = int(time())
            slow_queue_item = (failure_timestamp, message.wrap())
            self._slow_queue.push(txn, slow_queue_item)
            pmnc.log.debug("moving {0:s} from fast queue #{1:02d} to "
                           "slow queue".format(message, queue_idx))

    ###################################
    # this method is used by Resource instances to notify
    # the interface about a retried call just enqueued

    def raw_queue_alert(self):

        self._raw_work.add_work(0)

###############################################################################

class Resource(TransactionalResource): # "retry" resource for enqueueing calls in transactions

    def connect(self):

        self._attrs = []
        self._raw_queue = PersistentQueue("raw", 3072)
        self._retry_interface = pmnc.interfaces.get_interface("retry")
        TransactionalResource.connect(self)

    ###################################

    def begin_transaction(self, *args, **kwargs):

        TransactionalResource.begin_transaction(self, *args, **kwargs)
        self._txn, self._commit, self._rollback = pmnc.state.start_transaction(__name__)

    ###################################

    def __getattr__(self, name):

        self._attrs.append(name)
        return self

    ###################################

    def __call__(self, *args, **kwargs):

        attrs, self._attrs, self._message = self._attrs, [], None
        assert len(attrs) == 2, "expected module.method RPC syntax"
        module, method = attrs

        if not self.resource_args: # sync local call (xa.pmnc.module.method)
            assert not self.resource_args and \
                   not self.resource_kwargs, "synchronous local calls have no options"
            return pmnc.__getattr__(module).__getattr__(method)(*args, **kwargs)

        assert len(self.resource_args) == 1, "expected xa.pmnc(\"somecage\") syntax"
        cage = self.resource_args[0]

        if not cage.endswith(":retry"): # sync remote call (xa.pmnc("cage").module.method)
            assert not self.resource_kwargs, "synchronous remote calls have no options"
            return pmnc(cage).__getattr__(module).__getattr__(method)(*args, **kwargs)

        # async call (pmnc("...:retry").module.method)

        cage = cage[:-6]
        if cage != "":
            assert cage != __cage__, "pmnc(\":retry\") must be used to send " \
                                     "asynchronous calls to the cage itself"
            # remote call is reduced to local call to remote_call.transmit
            module, method, args, kwargs = \
                "remote_call", "transmit", (cage, module, method, args, kwargs), {}

        # each call can have an optional id provided by the client
        # to prevent duplicate execution of the same call

        custom_filtered_id = self.resource_kwargs.pop("id", None)
        assert custom_filtered_id is None or isinstance(custom_filtered_id, str), \
               "custom retry identifier must be an instance of str"
        filtered_id = self._make_filtered_id(custom_filtered_id)

        # the caller can also specify optional expiration time for this call

        expires_in = self.resource_kwargs.pop("expires_in", None)
        assert expires_in is None or isinstance(expires_in, float), \
               "expiration time must be an instance of float"
        deadline = expires_in is not None and int(time() + expires_in) or None

        assert not self.resource_kwargs, "invalid option for asynchronous call"

        # wrap up a message and push it to the persistent raw queue

        self._message = RetriedCallMessage(module, method, args, kwargs,
                                           deadline, filtered_id)

        self._txn = pmnc.state.explicit_transaction(__name__,
                        self._txn, self._raw_queue.push, self._message.wrap())[0]

        # the returned value is always unique and does not indicate
        # whether the attempt to execute the call is a duplicate,
        # this fact can only be determined later by the raw thread

        return self._message.unique_id

    ###################################

    @staticmethod
    def _make_filtered_id(custom_filtered_id):

        # if a retried call is initiated from within another retried call,
        # and the caller has provided its own unique id, the id is decorated
        # with the unique id of the currently executed retried call

        if custom_filtered_id is not None:
            retry_context = pmnc.request.parameters.get("retry")
            if retry_context is not None:
                return "{0:s}:{1:s}".format(retry_context["id"], custom_filtered_id)
            else:
                return custom_filtered_id
        else:
            return None

    ###################################

    def _get_retry_interface(self): # this method only exists to be overriden in self-tests

        return self._retry_interface

    ###################################

    def commit(self):

        self._commit(self._txn)

        if self._message:
            pmnc.log.info("request {0:s} has enqueued {1:s}".\
                          format(pmnc.request.unique_id, self._message))
            retry_interface = self._get_retry_interface()
            if retry_interface: # notify the interface
                retry_interface.raw_queue_alert()

    ###################################

    def rollback(self):

        self._rollback(self._txn)

###############################################################################

valid_retry_id = by_regex("RT-[0-9]{14}-[0-9A-F]{12}")

###############################################################################

# the following class encapsulates the retried call information,
# wrapped for persistent storage, then unwrapped and executed

class RetriedCallMessage:

    @typecheck
    def __init__(self, module: str, method: str, args: tuple, kwargs: dict,
                 deadline: optional(int),    # can be set to None but explicitly
                 filtered_id: optional(str), # can be set to None but explicitly
                 unique_id: optional(valid_retry_id) = None,
                 start: optional(int) = None,
                 attempt: optional(int) = None,
                 request_dict: optional(dict) = None):

        self._module = module
        self._method = method
        self._args = args
        self._kwargs = kwargs
        self._deadline = deadline
        self._filtered_id = filtered_id
        self._unique_id = unique_id or self._make_unique_id()
        self._start = start or int(time())
        self._attempt = attempt or 1
        if request_dict is None:
            request_dict = pmnc.request.to_dict()
            request_dict.pop("deadline")
        self._request_dict = request_dict

    unique_id = property(lambda self: self._unique_id)
    filtered_id = property(lambda self: self._filtered_id is None and self._unique_id or self._filtered_id)
    expired = property(lambda self: self._deadline is not None and time() > self._deadline)
    attempt = property(lambda self: self._attempt)

    def __eq__(self, other):
        return self._module == other._module and \
               self._method == other._method and \
               self._args == other._args and \
               self._kwargs == other._kwargs and \
               self._filtered_id == other._filtered_id and \
               self._deadline == other._deadline and \
               self._unique_id == other._unique_id and \
               self._start == other._start and \
               self._attempt == other._attempt and \
               self._request_dict == other._request_dict

    def __str__(self):
        if self._module == "remote_call" and self._method == "transmit":
            return "retried remote call {0[0]:s}.{0[1]:s}.{0[2]:s}({1:s}) as {2:s}".\
                   format(self._args, self._filtered_id or "", self._unique_id)
        else:
            return "retried local call {0:s}.{1:s}({2:s}) as {3:s}".\
                   format(self._module, self._method, self._filtered_id or "", self._unique_id)

    @staticmethod
    def _make_unique_id():
        current_time = strftime("%Y%m%d%H%M%S")
        random_id = b2a_hex(urandom(6)).decode("ascii").upper()
        return "RT-{0:s}-{1:s}".format(current_time, random_id)

    def wrap(self):
        return dict(module = self._module,
                    method = self._method,
                    args = self._args,
                    kwargs = self._kwargs,
                    deadline = self._deadline,
                    filtered_id = self._filtered_id,
                    unique_id = self._unique_id,
                    start = self._start,
                    attempt = self._attempt,
                    request_dict = self._request_dict)

    @classmethod
    def unwrap(cls, wrapped):
        return cls(wrapped["module"], wrapped["method"], wrapped["args"], wrapped["kwargs"],
                   wrapped["deadline"], wrapped["filtered_id"], wrapped["unique_id"],
                   wrapped["start"], wrapped["attempt"], wrapped["request_dict"])

    def tick_retry(self):
        self._attempt += 1

    def execute(self):

        # if the call has expired, exit silently and let the call be committed

        if self.expired:
            pmnc.log.warning("{0:s} has expired and will not "
                             "be retried any more".format(self))
            return False

        # temporarily impersonate the request being retried,
        # inheriting the original request's deadline

        original_request = pmnc.request
        impersonated_request = \
            pmnc.request.from_dict(self._request_dict,
                                   timeout = original_request.remain)

        pmnc.log.info("retry request {0:s} becomes {1:s} to make attempt "
                      "{2:d} of {3:s}, deadline in {4:.01f} second(s)".\
                      format(original_request.unique_id, impersonated_request.unique_id,
                             self._attempt, self, impersonated_request.remain))
        try:

            current_thread()._request = impersonated_request
            try:

                # inject retry information to the impersonated request context

                pmnc.request.parameters["retry"] = \
                    dict(id = self._unique_id, start = self._start,
                         attempt = self._attempt, deadline = self._deadline)

                # execute the target method

                result = pmnc.__getattr__(self._module).\
                              __getattr__(self._method)(*self._args, **self._kwargs)

            finally:
                current_thread()._request = original_request

        except:
            pmnc.log.error("retry request {0:s} has failed in {1:s}: {2:s}".\
                           format(original_request.unique_id, self, exc_string()))
            raise
        else:
            pmnc.log.info("retry request {0:s} has returned from {1:s}".\
                          format(original_request.unique_id, self))
            return self._intercept_result(result)

    _intercept_result = lambda self, x: True # to be overriden in self-tests

###############################################################################

def self_test_loopback(*args, **kwargs):

    if pmnc.request.self_test != __name__:
        raise Exception("invalid access to self-test code")

    if "fail" in kwargs:
        raise Exception(kwargs["fail"])

    return (args, kwargs, pmnc.request.to_dict())

_self_test_retried_queue = InterlockedQueue()

def self_test_retried(*args, **kwargs):

    if pmnc.request.self_test != __name__:
        raise Exception("invalid access to self-test code")

    if "fail" in kwargs:
        raise Exception(kwargs["fail"])

    retry_ctx = pmnc.request.parameters["retry"]
    if retry_ctx["attempt"] == 1 and kwargs.get("fail_first_attempt"):
        raise Exception("first attempt fails")

    _self_test_retried_queue.push((args, kwargs, pmnc.request.to_dict()))

###############################################################################

def self_test():

    from pmnc.request import fake_request
    from expected import expected
    from time import sleep
    from random import randint, normalvariate
    from hashlib import sha1

    ###################################

    rus = "\u0410\u0411\u0412\u0413\u0414\u0415\u0401\u0416\u0417\u0418\u0419" \
          "\u041a\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424" \
          "\u0425\u0426\u0427\u0428\u0429\u042c\u042b\u042a\u042d\u042e\u042f" \
          "\u0430\u0431\u0432\u0433\u0434\u0435\u0451\u0436\u0437\u0438\u0439" \
          "\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441\u0442\u0443\u0444" \
          "\u0445\u0446\u0447\u0448\u0449\u044c\u044b\u044a\u044d\u044e\u044f"

    ###################################
    # override the method in Resource so that its already created instances
    # rebind upon each call to the possibly restarted retry interface

    Resource._get_retry_interface = lambda self: pmnc.interfaces.get_interface("retry")

    request_timeout = pmnc.config_interfaces.get("request_timeout")

    ###################################

    def test_make_ids():

        fake_request(10.0)

        unique_id1 = RetriedCallMessage._make_unique_id()
        unique_id2 = RetriedCallMessage._make_unique_id()
        assert valid_retry_id(unique_id1) and valid_retry_id(unique_id2)
        assert unique_id1 != unique_id2

        ###############################

        assert Resource._make_filtered_id(None) is None
        assert Resource._make_filtered_id("foo") == "foo"
        assert Resource._make_filtered_id(rus) == rus
        pmnc.request.parameters["retry"] = { "id": "bar" }
        assert Resource._make_filtered_id("foo") == "bar:foo"
        assert Resource._make_filtered_id(rus) == "bar:" + rus

    test_make_ids()

    ###################################

    def test_large_messages():

        fake_request(10.0)

        q = PersistentQueue("large_q", Interface._large_queue_re_len)

        vs = [ urandom(1 << i) for i in range(20) ]

        for v in vs:
            pmnc.state.implicit_transaction(q.push, v)

        for v in vs:
            assert pmnc.state.implicit_transaction(q.peek) == v
            assert pmnc.state.implicit_transaction(q.pop) == v

    test_large_messages()

    ###################################

    def test_rc_message():

        fake_request(10.0)

        rcm = RetriedCallMessage("module", "method", () , {}, None, "filtered_id")
        rcm._intercept_result = lambda x: x

        assert valid_retry_id(rcm.unique_id)
        assert rcm.filtered_id == "filtered_id"
        assert not rcm.expired
        sleep(1.2)
        assert not rcm.expired
        assert rcm.attempt == 1
        assert str(rcm) == "retried local call module.method(filtered_id) as {0:s}".format(rcm.unique_id)
        rcm.tick_retry()
        assert rcm.attempt == 2
        assert RetriedCallMessage.unwrap(unpickle(pickle(rcm.wrap()))) == rcm

        ###############################

        rcm2 = RetriedCallMessage("remote_call", "transmit",
                                  ("cage", "module", "method", (), {}) , {},
                                  int(time() + 1.0), None)
        rcm2._intercept_result = lambda x: x

        assert rcm2.filtered_id == rcm2.unique_id
        assert not rcm2.expired
        sleep(1.2)
        assert rcm2.expired
        assert str(rcm2) == "retried remote call cage.module.method() as {0:s}".format(rcm2.unique_id)
        assert RetriedCallMessage.unwrap(unpickle(pickle(rcm2.wrap()))) == rcm2

        ###############################

        rcm3 = RetriedCallMessage(__name__, "self_test_loopback",
                                  ("1", 2) , { "foo": "bar" }, int(time() + 60.0), None)
        rcm3._intercept_result = lambda x: x
        start_rcm3 = time()

        old_request_id = pmnc.request.unique_id
        fake_request(10.0)
        new_request_id = pmnc.request.unique_id

        args, kwargs, request_dict = rcm3.execute()
        assert args == ("1", 2)
        assert kwargs == { "foo": "bar" }
        deadline = request_dict.pop("deadline")
        assert abs(deadline - time() - request_timeout) < 3.0
        retry_context = request_dict["parameters"].pop("retry")
        assert retry_context["id"] == rcm3.unique_id
        assert retry_context["attempt"] == 1
        assert abs(retry_context["start"] - start_rcm3) < 3.0
        assert abs(retry_context["deadline"] - (start_rcm3 + 60.0)) < 3.0
        assert request_dict == { "interface": "-", "protocol": "-",
                                 "parameters": { "auth_tokens": {} },
                                 "unique_id": old_request_id }

        ###############################

        rcm4 = RetriedCallMessage(__name__, "self_test_loopback",
                                  () , { "fail": "test" }, None, "foo")
        rcm4._intercept_result = lambda x: x
        with expected(Exception("test")):
            rcm4.execute()

    test_rc_message()

    ###################################

    def test_invalid_syntax():

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.pmnc.foo.bar.biz()
        with expected(AssertionError("expected module.method RPC syntax")):
            xa.execute()

    test_invalid_syntax()

    ###################################

    def test_invalid_use():

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.pmnc(foo = "bar").foo.bar()
        with expected(AssertionError("synchronous local calls have no options")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc("foo", "bar").foo.bar()
        with expected(AssertionError("expected xa.pmnc(\"somecage\") syntax")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc("somecage", foo = "bar").foo.bar()
        with expected(AssertionError("synchronous remote calls have no options")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc("somecage:retry", foo = "bar").foo.bar()
        with expected(AssertionError("invalid option for asynchronous call")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc(":retry", foo = "bar").foo.bar()
        with expected(AssertionError("invalid option for asynchronous call")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc("{0:s}:retry".format(__cage__), id = "123").foo.bar()
        with expected(AssertionError("pmnc(\":retry\") must be used to send asynchronous calls to the cage itself")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc(":retry", id = 123).foo.bar()
        with expected(AssertionError("custom retry identifier must be an instance of str")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.pmnc(":retry", expires_in = 123).foo.bar()
        with expected(AssertionError("expiration time must be an instance of float")):
            xa.execute()

    test_invalid_use()

    ###################################

    def test_sync_calls():

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.pmnc.__getattr__(__name__).self_test_loopback(1, "foo", biz = "baz")
        args, kwargs, request_dict = xa.execute()[0]
        assert args == (1, "foo")
        assert kwargs == { "biz": "baz" }
        assert request_dict["unique_id"] == pmnc.request.unique_id

        # testing RPC is a little ugly and does not really test
        # argument passing, but then it tests rollback

        xa = pmnc.transaction.create()
        xa.pmnc("such_cage_never_existed").foo.bar()
        with expected(Exception("no discovery response")):
            xa.execute()

    test_sync_calls()

    ###################################

    def test_async_push():

        fake_request(10.0)

        # local async call is enqueued as it is

        xa = pmnc.transaction.create()
        xa.pmnc(":retry").__getattr__(__name__).self_test_loopback(2, "bar", baz = "biz")
        unique_id = xa.execute()[0]
        message_start = time()
        assert valid_retry_id(unique_id)

        # now let's see what has been pushed

        raw_q = PersistentQueue("raw", Interface._large_queue_re_len)
        wrapped_message = pmnc.state.implicit_transaction(raw_q.pop)
        message = RetriedCallMessage.unwrap(wrapped_message)

        assert message._module == __name__
        assert message._method == "self_test_loopback"
        assert message._args == (2, "bar")
        assert message._kwargs == { "baz": "biz" }
        assert message.filtered_id == unique_id
        assert message.unique_id == unique_id
        assert message.attempt == 1
        assert abs(message_start - message._start) < 3.0
        request_dict = pmnc.request.to_dict()
        request_dict.pop("deadline")
        assert message._request_dict == request_dict

        ###############################

        # remote async call is enqueued as a local call to remote_call.transmit

        xa = pmnc.transaction.create()
        xa.pmnc("such_cage_never_existed:retry", id = rus).foo.bar()
        unique_id = xa.execute()[0]
        message_start = time()
        assert valid_retry_id(unique_id)

        # now let's see what has been pushed

        raw_q = PersistentQueue("raw", Interface._large_queue_re_len)
        wrapped_message = pmnc.state.implicit_transaction(raw_q.pop)
        message = RetriedCallMessage.unwrap(wrapped_message)

        assert message._module == "remote_call"
        assert message._method == "transmit"
        assert message._args == ("such_cage_never_existed", "foo", "bar", (), {})
        assert message._kwargs == {}
        assert message.filtered_id == rus
        assert message.unique_id == unique_id
        assert message.attempt == 1
        assert abs(message_start - message._start) < 3.0
        request_dict = pmnc.request.to_dict()
        request_dict.pop("deadline")
        assert message._request_dict == request_dict

    test_async_push()

    ###################################

    Interface._work_timeout = 2.0

    def start_interface():
        config = pmnc.config_interface_retry.copy()
        ifc = pmnc.interface.create("retry", **config)
        ifc._lazy_timeout = 5.0
        ifc.start()
        pmnc.interfaces.set_fake_interface("retry", ifc)
        return ifc

    def stop_interface(ifc):
        pmnc.interfaces.delete_fake_interface("retry")
        ifc.cease()
        ifc.stop()

    ###################################

    def test_start_stop():

        ifc = start_interface()
        sleep(10.0)
        stop_interface(ifc)

    test_start_stop()

    ###################################

    def test_retried_call_success():

        ifc = start_interface()
        try:

            fake_request(30.0)

            # initial success

            xa = pmnc.transaction.create()
            xa.pmnc(":retry", id = "call/1").__getattr__(__name__).self_test_retried()
            retry_id = xa.execute()[0]

            args, kwargs, request_dict = _self_test_retried_queue.pop(3.0)
            assert args == ()
            assert kwargs == {}
            assert request_dict["unique_id"] == pmnc.request.unique_id
            assert request_dict["parameters"]["retry"]["id"] == retry_id

            # already accepted

            xa = pmnc.transaction.create()
            xa.pmnc(":retry", id = "call/1").__getattr__(__name__).self_test_retried()
            retry_id = xa.execute()[0]

            assert _self_test_retried_queue.pop(3.0) is None

        finally:
            stop_interface(ifc)

    test_retried_call_success()

    ###################################

    def test_retried_call_accepted(): # depends on the previous test

        ifc = start_interface()
        try:

            fake_request(45.0)

            # already accepted, this time the record survived interface restart

            xa = pmnc.transaction.create()
            xa.pmnc(":retry", id = "call/1").__getattr__(__name__).self_test_retried()
            retry_id = xa.execute()[0]

            assert _self_test_retried_queue.pop(3.0) is None

            # but as time goes by, filter records that get older than
            # retention time are removed and duplicate execution is possible

            pmnc.log.info("sleeping {0:d} second(s)".format(int(ifc._retention_time)))
            sleep(ifc._retention_time)

            xa = pmnc.transaction.create()
            xa.pmnc(":retry", id = "call/1").__getattr__(__name__).self_test_retried()
            retry_id = xa.execute()[0]

            assert _self_test_retried_queue.pop(3.0) is not None

        finally:
            stop_interface(ifc)

    test_retried_call_accepted()

    ###################################

    def test_retried_call_failure():

        ifc = start_interface()
        try:

            fake_request(30.0)

            # initial failure

            xa = pmnc.transaction.create()
            xa.pmnc(":retry", id = "ID=\"{0:s}\"".format(rus)).__getattr__(__name__).self_test_retried(fail_first_attempt = True)
            retry_id = xa.execute()[0]

            assert _self_test_retried_queue.pop(3.0) is None

            # but then it is retried and succeeds

            pmnc.log.info("sleeping {0:d} second(s)".format(int(ifc._retry_interval)))
            sleep(ifc._retry_interval)

            args, kwargs, request_dict = _self_test_retried_queue.pop(3.0)
            assert args == ()
            assert kwargs == { "fail_first_attempt": True }
            assert request_dict["unique_id"] == pmnc.request.unique_id
            assert request_dict["parameters"]["retry"]["id"] == retry_id
            assert request_dict["parameters"]["retry"]["attempt"] == 2

        finally:
            stop_interface(ifc)

    test_retried_call_failure()

    ###################################

    def test_retried_call_expiration():

        ifc = start_interface()
        try:

            fake_request(30.0)

            xa = pmnc.transaction.create()
            xa.pmnc(":retry", id = "expired1", expires_in = 5.0).\
               __getattr__(__name__).self_test_retried(fail = "never succeeds")
            xa.execute()

            assert _self_test_retried_queue.pop(15.0) is None # nothing happens

            # but the call is put to one of the done queues (something could
            # have been left in the queues from the previous tests, therefore
            # we have to drain)

            for done_queue in ifc._done_queues:
                done_queue_item = pmnc.state.implicit_transaction(done_queue.pop)
                while done_queue_item is not None:
                    success_timestamp, filtered_id = done_queue_item
                    if filtered_id == "expired1":
                        assert abs(success_timestamp - (time() - 5.0)) < 5.0
                        break # while
                    done_queue_item = pmnc.state.implicit_transaction(done_queue.pop)
                else:
                    continue # for
                break # for
            else:
                assert False, "the call should have been cancelled"

        finally:
            stop_interface(ifc)

    test_retried_call_expiration()

    ###################################

    def test_offline():

        fake_request(30.0)

        # first the calls are enqueued

        pushed_ids = []

        for i in range(10):
            xa = pmnc.transaction.create()
            xa.pmnc(":retry").__getattr__(__name__).self_test_retried()
            pushed_ids.append(xa.execute()[0])

        pushed_ids.sort()

        # nothing happens yet

        assert _self_test_retried_queue.pop(3.0) is None

        # and then the interface is started

        ifc = start_interface()
        try:

            # raw thread wakes by itself (in _work_timeout)

            pmnc.log.info("sleeping {0:d} second(s)".format(int(ifc._work_timeout)))
            sleep(ifc._work_timeout)

            popped_ids = []

            for i in range(10):
                args, kwargs, request_dict = pmnc.request.pop(_self_test_retried_queue)
                popped_ids.append(request_dict["parameters"]["retry"]["id"])

            popped_ids.sort()

            assert _self_test_retried_queue.pop(3.0) is None
            assert pushed_ids == popped_ids

        finally:
            stop_interface(ifc)

    test_offline()

    ###################################

    def test_failing_retry():

        ifc = start_interface()
        try:

            fake_request(30.0)

            # make sure the interface will fail when attempting
            # to move messages to the slow queue

            pop_fail_queue = InterlockedQueue()

            def pop_fast_queue_failure(tx, queue_idx, unique_id):
                pop_fail_queue.push(unique_id)
                raise Exception("always fails")

            original_pop_fast_queue_failure = ifc._pop_fast_queue_failure
            ifc._pop_fast_queue_failure = pop_fast_queue_failure

            # now throw in a failing call

            xa = pmnc.transaction.create()
            xa.pmnc(":retry").__getattr__(__name__).self_test_retried(fail_first_attempt = True)
            retry_id = xa.execute()[0]

            # nothing happens yet, except for countless attempts to retry the message

            assert _self_test_retried_queue.pop(3.0) is None

            # restore the method

            ifc._pop_fast_queue_failure = original_pop_fast_queue_failure

            # then it is retried and succeeds

            pmnc.log.info("sleeping {0:d} second(s)".format(int(ifc._retry_interval + ifc._lazy_timeout)))
            sleep(ifc._retry_interval + ifc._lazy_timeout)

            args, kwargs, request_dict = _self_test_retried_queue.pop(3.0)

            # and it is still attempt 2

            assert request_dict["parameters"]["retry"]["id"] == retry_id
            assert request_dict["parameters"]["retry"]["attempt"] == 2

            # despite numerous attempts to retry

            failed_attempts = 0
            retried_id = pop_fail_queue.pop(0.0)
            while retried_id is not None:
                assert retried_id == retry_id
                failed_attempts += 1
                retried_id = pop_fail_queue.pop(0.0)

            assert failed_attempts > 10

        finally:
            stop_interface(ifc)

    test_failing_retry()

    ###################################

    def test_stress():

        started_calls = InterlockedQueue()

        avg_re_len = Interface._large_queue_re_len * 3 // 4
        re_len_dev = Interface._large_queue_re_len // 2

        def th_proc():
            while not current_thread().stopped():
                fake_request(10.0)
                data_len = max(1, int(normalvariate(avg_re_len, re_len_dev)))
                data = urandom(data_len)
                xa = pmnc.transaction.create()
                xa.pmnc(":retry").__getattr__(__name__).self_test_retried(data, fail_first_attempt = randint(0, 1))
                started_calls.push((xa.execute()[0], data))

        ifc = start_interface()
        try:

            fake_request(120.0)

            ths = [ HeavyThread(target = th_proc) for i in range(20) ]
            for th in ths: th.start()
            Timeout(10.0).wait()
            for th in ths: th.stop()

            pmnc.log.message("pushing has stopped")

            started_calls_list = []

            id_data = started_calls.pop(0.0)
            while id_data is not None:
                id, data = id_data
                started_calls_list.append((id, data))
                id_data = started_calls.pop(0.0)

            started_calls_list.sort()

            completed_calls_list = []

            t = pmnc.request.pop(_self_test_retried_queue)
            while len(completed_calls_list) < len(started_calls_list):
                if t is not None:
                    args, kwargs, request_dict = t
                    completed_calls_list.append((request_dict["parameters"]["retry"]["id"], args[0]))
                t = pmnc.request.pop(_self_test_retried_queue)

            pmnc.log.message("sleeping {0:d} second(s)".format(int(ifc._retry_interval + ifc._lazy_timeout)))
            sleep(ifc._retry_interval + ifc._lazy_timeout)

            assert _self_test_retried_queue.pop(3.0) is None

            completed_calls_list.sort()
            assert started_calls_list == completed_calls_list

        finally:
            stop_interface(ifc)

    pmnc._loader._set_log_priority(4)
    try:
        test_stress()
    finally:
        pmnc._loader._set_log_priority(6)

    ###################################

    def test_large_messages_performance():

        fake_request(10.0)

        q = PersistentQueue("large_q_perf", Interface._large_queue_re_len)

        def test_size(n):

            fake_request(30.0)
            t = Timeout(5.0)

            i = 0
            vs_pushed = []
            while not t.expired:
                v = ("0123456789"[i % 10] * n).encode("ascii"); i += 1
                pmnc.state.implicit_transaction(q.push, v)
                vs_pushed.append(sha1(v).hexdigest())

            vs_popped = []
            while True:
                v = pmnc.state.implicit_transaction(q.pop)
                if v is None:
                    break
                vs_popped.append(sha1(v).hexdigest())

            assert vs_pushed == vs_popped

            elapsed = pmnc.request.elapsed
            pmnc.log.message("message size: {0:d} byte(s), {1:.01f} push+pop "
                             "cycle(s)/sec".format(n, len(vs_pushed) / elapsed))

        for i in (256, 1024, 4096, 16384, 65536, 262144, 1048576):
            test_size(i)

    test_large_messages_performance()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF