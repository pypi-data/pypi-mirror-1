#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# Interlocked factory (counting created instances and allowing to wait for
# all existing instances to be destroyed).
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
################################################################################

__all__ = [ "InterlockedFactory" ]

################################################################################

import threading; from threading import Lock, Event

################################################################################

class InterlockedFactory:

    def __init__(self, factory):
        self._factory = factory
        self._stopped = Event()
        self._lock = Lock()
        self._count = 0
        self._zero = Event()
        self._zero.set()

    def _rcount(self):
        with self._lock:
            return self._count
    count = property(_rcount)

    def create(self, *args, **kwargs):
        with self._lock:
            if not self._stopped.is_set():
                result = self._factory(*args, **kwargs)
                self._count += 1
                self._zero.clear()
                return result
            else:
                return None

    def destroyed(self):
        with self._lock:
            self._count -= 1
            if self._count == 0:
                self._zero.set()

    def stop(self):
        with self._lock:
            assert not self._stopped.is_set()
            self._stopped.set()

    def wait(self, timeout = None):
        with self._lock:
            assert self._stopped.is_set()
        self._zero.wait(timeout)
        return self._zero.is_set()

################################################################################

if __name__ == "__main__":

    print("self-testing module interlocked_factory.py:")

    ###################################

    from expected import expected

    ###################################

    class Foo: pass

    ilf = InterlockedFactory(Foo)
    assert ilf.count == 0

    with expected(AssertionError):
        ilf.wait()

    f = ilf.create()
    assert isinstance(f, Foo)
    assert ilf.count == 1

    with expected(AssertionError):
        ilf.wait(1.0)

    with expected(TypeError):
        ilf.create("will throw")
    assert ilf.count == 1

    ilf.stop()
    with expected(AssertionError):
        ilf.stop()

    assert ilf.create() is None

    assert not ilf.wait(1.0)

    ilf.destroyed()
    assert ilf.count == 0

    assert ilf.wait(1.0)
    assert ilf.wait()

    ###################################

    print("ok")

################################################################################
# EOF
