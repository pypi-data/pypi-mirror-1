#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements a generic resource pool. The allocated resources
# are connectable (have connect/disconnect method pair) and can expire, upon
# a timeout or perhaps upon failure. The pool performs connecting before
# it gives out an allocated resource, reuses released resources until they
# expire and disconnects resources when they expire.
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Resource", "TransactionalResource", "SQLResource", "ResourcePool",
            "RegisteredResourcePool", "ResourcePoolEmpty", "ResourcePoolStopped" ]

###############################################################################

import threading; from threading import Lock, Event, current_thread
import decimal; from decimal import Decimal, localcontext, Inexact
import datetime; from datetime import datetime

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..")))

import typecheck; from typecheck import typecheck, callable, list_of, tuple_of, dict_of
import pmnc.timeout; from pmnc.timeout import Timeout
import pmnc.threads; from pmnc.threads import HeavyThread, LightThread
import pmnc.request; from pmnc.request import Request

###############################################################################

class Resource: # a minimal connectable resource implementation

    @typecheck
    def __init__(self, name: str):
        self.__name = name
        self.__expired = Event()

    name = property(lambda self: self.__name)

    def expire(self):
        self.__expired.set()

    def _expired(self):
        return self.__expired.is_set()

    expired = property (lambda self: self._expired())

    def connect(self):
        pass

    def disconnect(self):
        pass

###############################################################################

# usable resource with transactions-related methods, instances of subclasses
# of this class are allocated through pmnc.resource.create

class TransactionalResource(Resource):

    _default_idle_timeout = 30.0 # three times the default request timeout
    _default_max_age = 300.0     # ten times idle timeout
    _default_min_time = 0.0      # zero, to have no effect by default

    @typecheck
    def __init__(self, name: str):
        Resource.__init__(self, name)
        self.__idle_timeout = Timeout(self._default_idle_timeout)
        self.__max_age = Timeout(self._default_max_age)
        self.__min_time = self._default_min_time

    # the following methods allow allocated instances
    # to expire or not to expire within some time

    @typecheck
    def set_idle_timeout(self, idle_timeout: float):
        self.__idle_timeout.reset(idle_timeout)

    def reset_idle_timeout(self):
        self.__idle_timeout.reset()

    @typecheck
    def set_max_age(self, max_age: float):
        self.__max_age.reset(max_age)

    def _expired(self):
        return self.__idle_timeout.expired or self.__max_age.expired or \
               Resource._expired(self)

    def _rttl(self):
        return min(self.__idle_timeout.remain, self.__max_age.remain)

    ttl = property(_rttl)

    @typecheck
    def set_min_time(self, min_time: float):
        self.__min_time = min_time

    min_time = property(lambda self: self.__min_time)

    # knowing name and size of the pool from which this resource instance
    # has been dispensed from is beneficial when you need to allocate
    # private thread pool within a resource instance's method, see
    # protocol_cmdexec.py for example, and I'm limiting this knowledge to
    # name and size only, refusing to insert a reference to the pool itself

    def set_pool_info(self, pool_name, pool_size):
        self.__pool_name, self.__pool_size = pool_name, pool_size

    pool_name = property(lambda self: self.__pool_name)
    pool_size = property(lambda self: self.__pool_size)

    # see .shared/transaction.py which uses these methods

    @typecheck
    def begin_transaction(self, xid: str, *, source_module_name: str,
                          transaction_options: dict,
                          resource_args: tuple, resource_kwargs: dict):
        self.__xid, self.__source_module_name = xid, source_module_name
        self.__transaction_options = transaction_options
        self.__resource_args, self.__resource_kwargs = resource_args, resource_kwargs

    xid = property(lambda self: self.__xid)
    source_module_name = property(lambda self: self.__source_module_name)
    transaction_options = property(lambda self: self.__transaction_options)
    resource_args = property(lambda self: self.__resource_args)
    resource_kwargs = property(lambda self: self.__resource_kwargs)

    def commit(self): # override
        pass

    def rollback(self): # override
        pass

###############################################################################

class SQLResource(TransactionalResource):

    @typecheck
    def __init__(self, name: str, *, decimal_precision: (int, int)):
        TransactionalResource.__init__(self, name)
        self.__precision, self.__scale = decimal_precision
        self.__decimal_ref = Decimal(10 ** self.__precision - 1) / Decimal(10 ** self.__scale)

    precision = property(lambda self: self.__precision)
    scale = property(lambda self: self.__scale)

    ###################################

    def execute(self, *batch, **params) -> tuple_of(list):
        params = { k: self._py_to_sql(v) for k, v in params.items() }
        return tuple(self._execute(sql, params) for sql in batch)

    @typecheck
    def _execute(self, sql: str, params: dict) -> list_of(dict):
        result = []
        records = self._execute_sql(sql, **params)
        for record in records:
            result.append({ str(k): self._sql_to_py(v) for k, v in record.items() })
        return result

    ###################################

    _supported_types = set((type(None), int, Decimal, bool, datetime, str, bytes))

    ###################################

    def _py_to_sql(self, v):
        t = type(v)
        if t not in self._supported_types:
            raise TypeError("type {0:s} is not supported".format(t.__name__))
        return getattr(self, "_py_to_sql_{0:s}".format(t.__name__))(v)

    def _py_to_sql_NoneType(self, v):
        return v

    def _py_to_sql_int(self, v):
        if -9223372036854775808 <= v <= 9223372036854775807:
            return v
        else:
            raise ValueError("integer value too large")

    def _py_to_sql_Decimal(self, v):
        return self._ensure_decimal_in_range(v)

    def _py_to_sql_bool(self, v):
        return v

    def _py_to_sql_datetime(self, v):
        return v

    def _py_to_sql_str(self, v):
        return v

    def _py_to_sql_bytes(self, v):
        return v

    ###################################

    def _sql_to_py(self, v):
        while True:
            pv = getattr(self, "_sql_to_py_{0:s}".format(type(v).__name__),
                         self._sql_to_py_unknown)(v)
            if pv is v: break
            v = pv
        if type(v) in self._supported_types:
            return v
        else:
            raise TypeError("type {0:s} is not supported".format(type(v).__name__))

    def _sql_to_py_NoneType(self, v):
        return v

    def _sql_to_py_int(self, v):
        if -9223372036854775808 <= v <= 9223372036854775807:
            return v
        else:
            raise ValueError("integer value too large")

    def _sql_to_py_Decimal(self, v):
        return self._ensure_decimal_in_range(v)

    def _sql_to_py_bool(self, v):
        return v

    def _sql_to_py_datetime(self, v):
        return v

    def _sql_to_py_str(self, v):
        return v

    def _sql_to_py_bytes(self, v):
        return v

    def _sql_to_py_unknown(self, v):
        raise TypeError("type {0:s} cannot be converted".format(type(v).__name__))

    ###################################

    @typecheck
    def _ensure_decimal_in_range(self, v: Decimal) -> Decimal:
        with localcontext() as ctx:
            ctx.traps[Inexact] = True
            try:
                v.quantize(self.__decimal_ref)
            except Inexact:
                raise ValueError("decimal value too precise")
        if abs(v) > self.__decimal_ref:
            raise ValueError("decimal value too large")
        return v

###############################################################################

class ResourcePoolEmpty(Exception): pass
class ResourcePoolStopped(Exception): pass

###############################################################################

class ResourcePool: # a fixed size pool of resources

    @typecheck
    def __init__(self, name: str, factory: callable, size: int = 2147483647):
        self._name, self._factory, self._size = name, factory, size
        self._lock, self._stopped = Lock(), False
        self._free, self._busy, self._count = [], [], 0

    name = property(lambda self: self._name)
    size = property(lambda self: self._size)

    def rfree(self):
        with self._lock:
            return len(self._free)
    free = property(lambda self: self.rfree())

    def rbusy(self):
        with self._lock:
            return len(self._busy)
    busy = property(lambda self: self.rbusy())

    def _create(self):
        self._count += 1
        return self._factory("{0:s}/{1:d}".format(self._name, self._count))

    def _connect(self, resource):
        try:
            resource.connect()
        except:
            with self._lock:
                self._busy.remove(resource)
            raise

    def _disconnect(self, resource):
        try:
            resource.disconnect()
        except:
            pass
        with self._lock:
            try:
                self._busy.remove(resource)
            except ValueError:
                pass

    @typecheck
    def allocate(self) -> Resource:
        resource = None
        while True:
            if resource:
                self._disconnect(resource)
            with self._lock:
                if self._stopped:
                    raise ResourcePoolStopped("resource pool is stopped")
                if self._free:
                    resource = self._free.pop()
                    self._busy.append(resource)
                    if resource.expired:
                        continue
                    else:
                        return resource
                elif len(self._busy) < self._size:
                    resource = self._create()
                    self._busy.append(resource)
                else:
                    raise ResourcePoolEmpty("resource pool is empty")
            self._connect(resource)
            return resource

    @typecheck
    def release(self, resource: Resource):
        if not resource.expired:
            with self._lock:
                try:
                    self._busy.remove(resource)
                except ValueError:
                    return
                self._free.append(resource)
        else:
            self._disconnect(resource)

    def sweep(self):
        while True:
            with self._lock:
                for resource in self._free:
                    if resource.expired:
                        self._free.remove(resource)
                        self._busy.append(resource)
                        break
                else:
                    return
            self._disconnect(resource)

    def stop(self):
        with self._lock:
            self._stopped = True
            for resource in self._free + self._busy:
                resource.expire()
        self.sweep()

################################################################################

# all instances of this descendant class are registered in a global list
# and are periodically swept, having their expired resources disconnected

class RegisteredResourcePool(ResourcePool):

    _pools_lock = Lock()
    _pools = []

    def __init__(self, *args, **kwargs):
        with self._pools_lock:
            if not self._watchdog.is_alive():
                raise ResourcePoolStopped("all resource pools are stopped")
            ResourcePool.__init__(self, *args, **kwargs)
            self._pools.append(self)

    ################################### a separate thread schedules sweeping and stopping

    @classmethod
    def start_pools(cls, pools_sweep_period = 15.0):
        cls._pools_sweep_period = pools_sweep_period
        cls._watchdog = HeavyThread(target = cls._watchdog_proc,
                                    name = "resource_pool")
        cls._watchdog.start()

    @classmethod
    def stop_pools(cls):
        if hasattr(cls, "_watchdog"): # has started
            cls._watchdog.stop()

    @classmethod
    def _watchdog_proc(cls):
        timeout = 0.0
        while not current_thread().stopped(timeout):
            with cls._pools_lock:
                timeout = cls._pools_sweep_period / (len(cls._pools) or 1)
                pool = cls._pools and cls._pools.pop(0) or None
            if pool:
                if cls._execute_proc(cls._sweep_proc, pool):
                    with cls._pools_lock:
                        cls._pools.append(pool)
        with cls._pools_lock:
            while cls._pools:
                pool = cls._pools.pop(0)
                cls._execute_proc(cls._stop_proc, pool)

    ################################### the actual processing is done by one-time threads

    # the one-time threads needs to have a request attached just in case
    # the disconnect() methods of some resources depend on it

    @classmethod
    def _execute_proc(cls, proc, pool):
        proc_name = proc.__name__.split("_", 2)[1]
        th = LightThread(target = proc, args = (pool, ),
                         name = "{0:s}:{1:s}".format(pool.name, proc_name))
        th._request = Request(interface = "__stop__", protocol = "n/a",
                              timeout = cls._pools_sweep_period)
        th.start()
        th.join(cls._pools_sweep_period)
        return not th.is_alive()

    @classmethod
    def _sweep_proc(cls, pool):
        pool.sweep()

    @classmethod
    def _stop_proc(cls, pool):
        pool.stop()

################################################################################

if __name__ == "__main__":

    print("self-testing module resource_pool.py:")

    ###################################

    import time
    import random

    from expected import expected
    from typecheck import InputParameterError, ReturnValueError

    ###################################

    # resources must be subclassed from Resource

    class NotAResource:
        def __init__(self, name):
            pass
        def connect(self):
            pass

    rp = ResourcePool("PoolName", NotAResource, 1)

    with expected(ReturnValueError("allocate() has returned an incompatible value: <__main__.NotAResource object")):
        rp.allocate()

    with expected(InputParameterError("release() has got an incompatible value for resource: <__main__.NotAResource object")):
        rp.release(NotAResource("foo"))

    ###################################

    class FooResource(Resource):

        def connect(self):
            time.sleep(random.random() * 0.1)

        def disconnect(self):
            time.sleep(random.random() * 0.1)

    ###################################

    # zero-sized pool will fail to allocate anything

    rp = ResourcePool("PoolName", FooResource, 0)

    with expected(ResourcePoolEmpty):
        rp.allocate()

    ###################################

    # resource instances name decoration

    rp = ResourcePool("PoolName", FooResource, 1)

    r = rp.allocate()
    assert r.name == "PoolName/1"
    rp.release(r)

    r = rp.allocate()
    assert r.name == "PoolName/1"
    r.expire()
    rp.release(r)

    r = rp.allocate()
    assert r.name == "PoolName/2"

    ###################################

    # resource reuse and overallocation

    rp = ResourcePool("PoolName", FooResource, 1)

    r1 = rp.allocate()
    rp.release(r1)

    r2 = rp.allocate()
    assert r2 is r1

    with expected(ResourcePoolEmpty):
        rp.allocate()

    ###################################

    # a pool can allocate an expired resource

    class BizResource(Resource):
        def connect(self):
            self.expire()

    rp = ResourcePool("PoolName", BizResource, 1)

    r1 = rp.allocate()
    assert r1.expired and rp.busy == 1
    rp.release(r1)
    assert rp.free == 0

    r2 = rp.allocate()
    assert r2 is not r1

    ###################################

    # the resources are reused in LIFO fashion

    rp = ResourcePool("PoolName", FooResource, 5)

    assert rp.free == 0 and rp.busy == 0

    r1 = rp.allocate()
    r2 = rp.allocate()
    r3 = rp.allocate()
    r4 = rp.allocate()
    r5 = rp.allocate()

    assert rp.free == 0 and rp.busy == 5

    rp.release(r4)
    rp.release(r3)
    rp.release(r5)
    rp.release(r1)
    rp.release(r2)

    assert rp.free == 5 and rp.busy == 0

    r2.expire()
    r3.expire()
    r5.expire()

    assert rp.free == 5 and rp.busy == 0

    assert rp.allocate() is r1

    assert rp.free == 3 and rp.busy == 1

    assert rp.allocate() is r4

    assert rp.free == 0 and rp.busy == 2

    assert rp.allocate() not in (r2, r3, r5)

    ###################################

    # stopped pool releases but does not allocate

    rp = ResourcePool("PoolName", FooResource, 2)

    r1 = rp.allocate()
    r2 = rp.allocate()

    rp.release(r1)

    assert rp.free == 1 and rp.busy == 1

    rp.stop()

    assert rp.free == 0 and rp.busy == 1

    rp.release(r2)

    assert rp.free == 0 and rp.busy == 0

    with expected(ResourcePoolStopped):
        rp.allocate()

    ###################################

    # sweeping disconnects expired resources

    rp = ResourcePool("PoolName", FooResource, 5)

    assert rp.free == 0 and rp.busy == 0

    r1 = rp.allocate()
    r2 = rp.allocate()
    r3 = rp.allocate()
    r4 = rp.allocate()
    r5 = rp.allocate()

    assert rp.free == 0 and rp.busy == 5

    rp.release(r4)
    rp.release(r3)
    rp.release(r5)
    rp.release(r1)
    rp.release(r2)

    assert rp.free == 5 and rp.busy == 0

    r2.expire()
    r3.expire()
    r5.expire()

    assert rp.free == 5 and rp.busy == 0

    rp.sweep()

    assert rp.free == 2 and rp.busy == 0

    ###################################

    # see how transactional resources are supposed to be used

    class BarResource(TransactionalResource): pass

    rp = ResourcePool("PoolName", BarResource, 1)

    r = rp.allocate()
    r.set_pool_info(rp.name, rp.size)
    assert r.pool_name == rp.name and r.pool_size == rp.size
    r.begin_transaction("xid", source_module_name = "module",
                        transaction_options = dict(foo = "bar"),
                        resource_args = (1, 2, 3), resource_kwargs = dict(biz = "baz"))
    assert r.xid == "xid"
    assert r.source_module_name == "module"
    assert r.transaction_options == dict(foo = "bar")
    assert r.resource_args == (1, 2, 3)
    assert r.resource_kwargs == dict(biz = "baz")
    r.commit()
    r.rollback()

    ###################################

    class FooTransactionalResource(TransactionalResource):

        _default_idle_timeout = 1.0
        _default_max_age = 3.5

    ftr = FooTransactionalResource("foores")

    assert ftr.min_time == 0.0
    ftr.set_min_time(1.0)
    assert ftr.min_time == 1.0

    assert not ftr.expired    # +0.01 new
    time.sleep(0.6)           # +0.62
    assert not ftr.expired    # +0.63 fresh
    assert ftr.ttl <= 0.5     # +0.64
    time.sleep(0.6)           # +1.25
    assert ftr.expired        # +1.26 idle timeout
    assert ftr.ttl == 0.0     # +1.27

    ftr.reset_idle_timeout()  # +1.28

    assert not ftr.expired    # +1.29 fresh
    time.sleep(0.6)           # +1.90
    assert not ftr.expired    # +1.91 fresh
    assert ftr.ttl <= 0.5     # +1.92
    time.sleep(0.6)           # +2.53
    assert ftr.expired        # +2.54 idle timeout
    assert ftr.ttl == 0.0     # +2.55

    ftr.set_idle_timeout(0.5) # +2.56

    assert not ftr.expired    # +2.57 fresh
    time.sleep(0.6)           # +3.18
    assert ftr.expired        # +3.19 idle timeout
    assert ftr.ttl == 0.0     # +3.20

    ftr.reset_idle_timeout()  # +3.21

    assert not ftr.expired    # +3.22 fresh
    time.sleep(0.6)           # +3.83
    assert ftr.expired        # +3.84 idle and too old
    assert ftr.ttl == 0.0     # +3.85

    ftr.reset_idle_timeout()  # +3.86

    assert ftr.expired        # +3.87 too old
    assert ftr.ttl == 0.0     # +3.88

    ################################### and now for something completely different

    # connect() allocates another resource

    class Res(Resource):
        def connect(self):
            self._res = rp.allocate()

    # fails no matter what the size of the pool is

    rp = ResourcePool("PoolName", Res, 100)
    with expected(ResourcePoolEmpty("resource pool is empty")):
        rp.allocate()

    assert rp.free == 0 and rp.busy == 0

    ###################################

    # connect() releases itself

    class Res(Resource):
        def connect(self):
            rp.release(self)
        def disconnect(self):
            raise Exception("should not see me")

    rp = ResourcePool("PoolName", Res, 1)
    r = rp.allocate()

    assert rp.free == 1 and rp.busy == 0

    rp.release(r) # does nothing

    ###################################

    # connect() releases itself with expiration

    r_disconnected = Event()

    class Res(Resource):
        def connect(self):
            self.expire()
            rp.release(self)
        def disconnect(self):
            r_disconnected.set()

    rp = ResourcePool("PoolName", Res, 1)
    r = rp.allocate()

    assert rp.free == 0 and rp.busy == 0 and r_disconnected.is_set()

    rp.release(r) # does nothing

    ###################################

    # disconnect() releases itself

    class Res(Resource):
        def disconnect(self):
            rp.release(self)

    rp = ResourcePool("PoolName", Res, 1)
    r = rp.allocate()
    r.expire()

    # causes infinite recursion, but the exception is ignored in _disconnect

    rp.release(r)

    ###################################

    N = 50   # number of threads
    T = 30.0 # number of seconds

    class FailingProvider: # this class makes sure the pool never overcommits the resources

        _lock = Lock()
        _conn = 0

        @classmethod
        def connect(cls):

            time.sleep(random.random() * 0.25)
            if random.random() < 0.05:
                raise Exception("some exception")
            time.sleep(random.random() * 0.25)

            with cls._lock:
                assert cls._conn < N
                cls._conn += 1

        @classmethod
        def disconnect(cls):

            with cls._lock:
                cls._conn -= 1

            time.sleep(random.random() * 0.25)
            if random.random() < 0.1:
                raise Exception("some exception")
            time.sleep(random.random() * 0.25)

    p = FailingProvider()

    class FailingResource(Resource):

        def connect(self):
            p.connect()

        def disconnect(self):
            p.disconnect()

        def use(self):
            time.sleep(random.random() * 0.1)
            if random.random() < 0.05:
                self.expire()

    rp = ResourcePool("PoolName", FailingResource, N)

    def th_proc():
        t = Timeout(T)
        while not t.expired:
            try:
                r = rp.allocate()
            except Exception as e:
                assert str(e) == "some exception", str(e)
                continue
            try:
                r.use()
            finally:
                rp.release(r)

    ths = [ threading.Thread(target = th_proc) for i in range(N) ]

    for th in ths:
        th.start()

    # underway

    for th in ths:
        th.join()

    ###################################

    # registered resources are periodically swept

    RegisteredResourcePool.start_pools(0.5)
    try:

        class FooPool(RegisteredResourcePool):
            def __init__(self, *args, **kwargs):
                RegisteredResourcePool.__init__(self, *args, **kwargs)
                self._sweep_count = 0
            def sweep(self):
                self._sweep_count += 1
                RegisteredResourcePool.sweep(self)

        foo_pool = FooPool("FooPool", Resource)

        class BarPool(RegisteredResourcePool):
            def __init__(self, *args, **kwargs):
                RegisteredResourcePool.__init__(self, *args, **kwargs)
                self._sweep_count = 0
            def sweep(self):
                self._sweep_count += 1
                RegisteredResourcePool.sweep(self)

        bar_pool = BarPool("BarPool", Resource)

        time.sleep(2.0)

    finally:
        RegisteredResourcePool.stop_pools()

    assert foo_pool._sweep_count > 2 and bar_pool._sweep_count > 2
    assert foo_pool._stopped and bar_pool._stopped

    with expected(ResourcePoolStopped("all resource pools are stopped")):
        BarPool("BarPool", Resource)

    ###################################

    # pools once hung upon sweeping are swept no more

    RegisteredResourcePool.start_pools(0.5)
    try:

        class GoodPool(RegisteredResourcePool):
            def __init__(self, *args, **kwargs):
                RegisteredResourcePool.__init__(self, *args, **kwargs)
                self._sweep_count = 0
            def sweep(self):
                self._sweep_count += 1
                RegisteredResourcePool.sweep(self)

        good_pool = FooPool("GoodPool", Resource)

        class BadPool(RegisteredResourcePool):
            def __init__(self, *args, **kwargs):
                RegisteredResourcePool.__init__(self, *args, **kwargs)
                self._sweep_count = 0
            def sweep(self):
                self._sweep_count += 1
                time.sleep(3600.0) # hangs
                RegisteredResourcePool.sweep(self)

        bad_pool = BadPool("BadPool", Resource)

        time.sleep(2.0)

    finally:
        RegisteredResourcePool.stop_pools()

    assert good_pool._sweep_count > 2 and bad_pool._sweep_count == 1
    assert good_pool._stopped and not bad_pool._stopped

    ###################################

    class SomeSQLResource(SQLResource):
        def _execute_sql(self, sql, **params):
            return eval(sql.format(**params))

    sqlr = SomeSQLResource("sqlres", decimal_precision = (5, 2))

    assert sqlr.precision == 5
    assert sqlr.scale == 2

    # basic behaviour and parameter ordering

    assert sqlr.execute() == ()
    assert sqlr.execute("[]") == ([],)
    assert sqlr.execute("[]", "[]") == ([], [])
    assert sqlr.execute("[{{1:2}}]") == ([{"1":2}],)
    assert sqlr.execute("[{{'foo': 'bar'}}]", notused = "123") == ([{"foo":"bar"}],)

    assert sqlr.execute("[dict(i={i})]", i=123) == ([{"i":123}],)
    assert sqlr.execute("[dict(i={i}, j={i})]", i=123) == ([{"i":123, "j":123}],)
    assert sqlr.execute("[dict(i={i}), dict(i={i})]", i=123) == ([{"i":123}, {"i":123}],)
    assert sqlr.execute("[dict(i={i1}), dict(i={i2})]", i1=123, i2=456) == ([{"i":123}, {"i":456}],)

    assert sqlr.execute("[dict(i={i})]", "[dict(i={i})]", i = 123) == ([{"i":123}], [{"i":123}])
    assert sqlr.execute("[dict(i={i})]", "[dict(i={j})]", i = 0, j = 1) == ([{"i":0}], [{"i":1}])
    assert sqlr.execute("[dict(i={i1}, j={j1})]", "[]", "[dict(i={i2}), dict(j={j2})]",
                       i1 = 1, i2 = 2, j1 = 3, j2 = 4) == ([{"i":1, "j":3}], [], [{"i":2}, {"j":4}])

    # NoneType

    assert sqlr.execute("[dict(n={n})]", n = None) == ([{"n":None}],)

    # int

    assert sqlr.execute("[dict(i={i})]", i = -9223372036854775808) == ([{"i":-9223372036854775808}],)
    assert sqlr.execute("[dict(i={i})]", i = 9223372036854775807) == ([{"i":9223372036854775807}],)
    with expected(ValueError("integer value too large")):
        sqlr.execute("", i = -9223372036854775809)
    with expected(ValueError("integer value too large")):
        sqlr.execute("", i = 9223372036854775808)
    with expected(ValueError("integer value too large")):
        sqlr.execute("[dict(i=-9223372036854775809)]")
    with expected(ValueError("integer value too large")):
        sqlr.execute("[dict(i=9223372036854775808)]")

    # Decimal

    assert sqlr.execute("[dict(d=Decimal('{d}'))]", d = Decimal("1.0")) == ([{"d":Decimal("1.0")}],)
    assert sqlr.execute("[dict(d=Decimal('{d}'))]", d = Decimal("999.99")) == ([{"d":Decimal("999.99")}],)
    assert sqlr.execute("[dict(d=Decimal('{d}'))]", d = Decimal("-999.99")) == ([{"d":Decimal("-999.99")}],)

    with expected(ValueError("decimal value too large")):
        sqlr.execute("", d = Decimal("1000.0"))
    with expected(ValueError("decimal value too large")):
        sqlr.execute("", d = Decimal("-1000.0"))
    with expected(ValueError("decimal value too precise")):
        sqlr.execute("", d = Decimal("0.001"))
    with expected(ValueError("decimal value too precise")):
        sqlr.execute("", d = Decimal("-0.001"))

    with expected(ValueError("decimal value too large")):
        sqlr.execute("[dict(d=Decimal('1000.0'))]")
    with expected(ValueError("decimal value too large")):
        sqlr.execute("[dict(d=Decimal('-1000.0'))]")
    with expected(ValueError("decimal value too precise")):
        sqlr.execute("[dict(d=Decimal('0.001'))]")
    with expected(ValueError("decimal value too precise")):
        sqlr.execute("[dict(d=Decimal('-0.001'))]")

    # bool

    assert sqlr.execute("[dict(b={b})]", b = True) == ([{"b":True}],)
    assert sqlr.execute("[dict(b={b})]", b = False) == ([{"b":False}],)

    # datetime

    dt = datetime.now()
    assert sqlr.execute("[dict(dt=datetime.strptime('{dt}', '%Y-%m-%d %H:%M:%S.%f'))]", dt = dt) == ([{"dt":dt}],)

    # str

    assert sqlr.execute("[dict(s='{s}')]", s = "foo") == ([{"s":"foo"}],)
    assert sqlr.execute("[dict(empty='{s}')]", s = "") == ([{"empty":""}],)

    # bytes

    assert sqlr.execute("[dict(b={b})]", b = b"bar") == ([{"b":b"bar"}],)
    assert sqlr.execute("[dict(empty={b})]", b = b"") == ([{"empty":b""}],)

    # unsupported type

    with expected(TypeError("type float is not supported")):
        sqlr.execute("", f = 1.0)
    with expected(TypeError("type float cannot be converted")):
        sqlr.execute("[dict(f=1.0)]")

    class SomeType:
        pass

    with expected(TypeError("type SomeType is not supported")):
        sqlr.execute("", f = SomeType())
    with expected(TypeError("type SomeType cannot be converted")):
        sqlr.execute("[{{None:SomeType()}}]")

    # custom + continuous conversion

    class TypeWrapper:
        def __init__(self, value):
            self._value = value
        value = property(lambda self: self._value)

    class OtherSQLResource(SQLResource):
        def _execute_sql(self, sql, **params):
            return eval(sql.format(**params))
        def _sql_to_py_TypeWrapper(self, v):
            return v.value

    osqlr = OtherSQLResource("osqlres", decimal_precision = (3, 1))

    assert osqlr.execute("[{{None:TypeWrapper(Decimal('0.0'))}}]") == ([{"None":Decimal("0.0")}],)
    assert osqlr.execute("[{{None:TypeWrapper(Decimal('99.9'))}}]") == ([{"None":Decimal("99.9")}],)
    assert osqlr.execute("[{{None:TypeWrapper(Decimal('-99.9'))}}]") == ([{"None":Decimal("-99.9")}],)

    with expected(ValueError("decimal value too large")):
        osqlr.execute("[{{None:TypeWrapper(Decimal('100.0'))}}]")
    with expected(ValueError("decimal value too large")):
        osqlr.execute("[{{None:TypeWrapper(Decimal('-100.0'))}}]")
    with expected(ValueError("decimal value too precise")):
        osqlr.execute("[{{None:TypeWrapper(Decimal('0.01'))}}]")
    with expected(ValueError("decimal value too precise")):
        osqlr.execute("[{{None:TypeWrapper(Decimal('-0.01'))}}]")

    assert osqlr.execute("[{{0:TypeWrapper(0)}}]") == ([{"0":0}],)
    assert osqlr.execute("[{{1:TypeWrapper(2**63-1)}}]") == ([{"1":2**63-1}],)
    assert osqlr.execute("[{{2:TypeWrapper(-2**63)}}]") == ([{"2":-2**63}],)
    with expected(ValueError("integer value too large")):
        osqlr.execute("[{{1:TypeWrapper(2**63)}}]")
    with expected(ValueError("integer value too large")):
        osqlr.execute("[{{1:TypeWrapper(-2**63-1)}}]")

    # unsupported conversion

    with expected(TypeError("type float cannot be converted")):
        osqlr.execute("[{{None:TypeWrapper(1.0)}}]")

    ###################################

    print("ok")

################################################################################
# EOF
