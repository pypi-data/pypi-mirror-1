#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module is a dispenser of thread pools and resource pools (which are
# grouped in pairs) and used by the transaction machinery and other modules
# that need them a private thread pool for something.
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
################################################################################

__all__ = [ "get_thread_pool", "get_resource_pool", "get_private_thread_pool" ]
__reloadable__ = False

################################################################################

import threading; from threading import Lock

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import typecheck; from typecheck import typecheck, optional, callable
import pmnc.thread_pool; from pmnc.thread_pool import ThreadPool
import pmnc.resource_pool; from pmnc.resource_pool import RegisteredResourcePool

###############################################################################

# module-level state => not reloadable

_private_pools = {}
_combined_pools = {}
_pools_lock = Lock()

###############################################################################

@typecheck
def _get_resource_config(resource_name: str) -> dict:

    # resources with names like "rpc__cage" share the same base configuration
    # of "config_resource_rpc" and have pool__resource_name=cage parameter added
    #                     ^^^                               ^^^^

    if "__" in resource_name:
        config_name, resource_name = resource_name.split("__", 1)
        config_module_name = "config_resource_{0:s}".format(config_name)
        config = pmnc.__getattr__(config_module_name).copy()
        config["pool__resource_name"] = resource_name
    else:
        config_module_name = "config_resource_{0:s}".format(resource_name)
        config = pmnc.__getattr__(config_module_name).copy()

    return config

###############################################################################

@typecheck
def _get_resource_factory(resource_name: str, pool_size: int) -> callable:

    def resource_factory(resource_instance_name):

        # fetch the configuration at the time of resource creation

        config = _get_resource_config(resource_name)

        # strip the pool__... meta settings ignoring static
        # setting pool__size which is already in effect

        idle_timeout = config.pop("pool__idle_timeout", None)
        max_age = config.pop("pool__max_age", None)
        min_time = config.pop("pool__min_time", None)
        if config.pop("pool__size", pool_size) != pool_size:
            pmnc.log.warning("change in pool size for resource {0:s} at "
                             "runtime has no effect".format(resource_name))

        pmnc.log.debug("creating resource instance {0:s}".format(resource_instance_name))

        # pass the rest of the config to the specific resource-creating factory

        resource_instance = pmnc.resource.create(resource_instance_name, **config)

        # if the meta settings have been present, adjust the created instance

        if idle_timeout is not None: resource_instance.set_idle_timeout(idle_timeout)
        if max_age is not None: resource_instance.set_max_age(max_age)
        if min_time is not None: resource_instance.set_min_time(min_time)
        resource_instance.set_pool_info(resource_name, pool_size)

        pmnc.log.debug("resource instance {0:s} has been created".\
                       format(resource_instance_name))

        return resource_instance

    return resource_factory

###############################################################################
# This method returns (creating if necessary) a pair of a thread pool and
# resource pool for the specified resource.

@typecheck
def _get_pools(resource_name: str) -> (ThreadPool, RegisteredResourcePool):

    pool_name = resource_name

    with _pools_lock:

        if pool_name not in _combined_pools:

            config = _get_resource_config(resource_name)

            # pool size for a resource is a static setting and is by default
            # equal to the number of the interfaces worker threads

            pool_size = config.get("pool__size") or \
                        pmnc.config_interfaces.get("thread_count")

            # create and cache new thread pool and resource pool for the resource,
            # they are of the same size, so that each thread can always pick a resource

            resource_factory = _get_resource_factory(resource_name, pool_size)

            thread_pool = ThreadPool(resource_name, pool_size)
            resource_pool = RegisteredResourcePool(resource_name, resource_factory, pool_size)

            _combined_pools[pool_name] = (thread_pool, resource_pool)

        return _combined_pools[pool_name]

###############################################################################

def get_thread_pool(resource_name: str) -> ThreadPool:
    return _get_pools(resource_name)[0]

###############################################################################

def get_resource_pool(resource_name: str) -> RegisteredResourcePool:
    return _get_pools(resource_name)[1]

###############################################################################

def get_private_thread_pool(pool_name: optional(str) = None,
                            pool_size: optional(int) = None,
                            *, __source_module_name) -> ThreadPool:

    pool_name = "{0:s}{1:s}".format(__source_module_name,
                                    pool_name is not None and "/{0:s}".format(pool_name) or "")

    with _pools_lock:

        if pool_name not in _private_pools:
            pool_size = pool_size or pmnc.config_interfaces.get("thread_count")
            _private_pools[pool_name] = ThreadPool(pool_name, pool_size)

        return _private_pools[pool_name]

###############################################################################

def self_test():

    from pmnc.request import fake_request
    from time import sleep
    from expected import expected

    ###################################

    def test_pools():

        tp1 = pmnc.shared_pools.get_thread_pool("test")
        tp2 = pmnc.shared_pools.get_thread_pool("test")
        assert tp1 is tp2

        assert list(_combined_pools.keys()) == [ "test" ]
        assert list(_private_pools.keys()) == []

        rp1 = pmnc.shared_pools.get_resource_pool("test")
        rp2 = pmnc.shared_pools.get_resource_pool("test")
        assert rp1 is rp2

        r = rp1.allocate()
        assert r.pool_name == "test" and r.pool_size == 3
        rp1.release(r)

    test_pools()

    ###################################

    def test_private_pool():

        tp1 = pmnc.shared_pools.get_private_thread_pool("foo")
        assert tp1.size == pmnc.config_interfaces.get("thread_count")

        tp2 = pmnc.shared_pools.get_private_thread_pool("foo", 10000)
        assert tp2 is tp1

        assert list(_combined_pools.keys()) == [ "test" ]
        assert list(_private_pools.keys()) == [ "shared_pools/foo" ]

        tp3 = pmnc.shared_pools.get_private_thread_pool(None, 3)
        assert tp3 is not tp2
        assert tp3.size == 3

        assert list(_combined_pools.keys()) == [ "test" ]
        assert list(sorted(_private_pools.keys())) == [ "shared_pools", "shared_pools/foo" ]

        def wu_test():
            return "123"

        wu = tp1.enqueue(fake_request(1.0), wu_test, (), {})
        assert wu.wait() == "123"

    test_private_pool()

    ###################################

    # utility function

    begin_transaction = \
        lambda r: r.begin_transaction("xid", source_module_name = __name__,
                                      transaction_options = {}, resource_args = (),
                                      resource_kwargs = {})

    # the following test relies on config_resource_test.py to contain
    # pool__size = 3
    # pool__idle_timeout = 1.0
    # pool__max_age = 2.0

    def test_expiration():

        def use(r):
            begin_transaction(r); r.execute(); r.reset_idle_timeout(); r.commit()

        rp = pmnc.shared_pools.get_resource_pool("test")
        assert rp.size == 3

        r1 = rp.allocate()
        use(r1)
        rp.release(r1)

        r2 = rp.allocate()
        assert r1 is r2 # +0.01 reused
        use(r2)
        rp.release(r2)

        sleep(1.1)

        r3 = rp.allocate()
        assert r3 is not r1 # +1.11 expired idle
        use(r3)
        rp.release(r3)

        sleep(0.6)

        r4 = rp.allocate()
        assert r4 is r3 # +0.61 reused
        use(r4)
        rp.release(r4)

        sleep(0.6)

        r5 = rp.allocate()
        assert r5 is r3 # +1.12 reused
        use(r5)
        rp.release(r5)

        sleep(0.6)

        r6 = rp.allocate()
        assert r6 is r3 # +1.73 reused
        use(r6)
        rp.release(r6)

        sleep(0.6)

        r7 = rp.allocate()
        assert r7 is not r3 # +2.34 expired max age
        use(r7)
        rp.release(r7)

    test_expiration()

    ###################################

    def test_execute():

        def wu_exec(res_name, *args, **kwargs):
            rp = pmnc.shared_pools.get_resource_pool(res_name)
            r = rp.allocate()
            if pmnc.request.remain < r.min_time: # this is similar to what
                raise Exception("declined")      # transaction.py does
            begin_transaction(r)
            result = r.execute(*args, **kwargs)
            r.commit()
            rp.release(r)
            return result

        rq = fake_request(3.0)
        tp = pmnc.shared_pools.get_thread_pool("test")

        wu = tp.enqueue(rq, wu_exec, ("test", 123), {"biz": "baz"})
        res = wu.wait()
        assert res["args"] == (123, )
        assert res["kwargs"] == {"biz": "baz"}
        assert res["config"] == {"p1": "v1", "p2": "v2"}

        wu = tp.enqueue(rq, wu_exec, ("test__foo", 123), {"biz": "baz"})
        res = wu.wait()
        assert res["args"] == (123, )
        assert res["kwargs"] == {"biz": "baz"}
        assert res["config"] == {"p1": "v1", "p2": "v2", "pool__resource_name": "foo"}

        # the following test relies on config_resource_test.py to contain
        # pool__min_time = 0.5

        sleep(rq.remain - 0.4)

        with expected(Exception("declined")):
            tp.enqueue(rq, wu_exec, ("test", ), {}).wait()

    test_execute()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF