#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements a simple class encapsulating a timeout concept.
# Timeout can be created, reset and used for waiting for an event or a queue
# for a limited amount of time.
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
################################################################################

__all__ = [ "Timeout" ]

################################################################################

import threading; from threading import Lock, Event
import time; from time import time
import random; from random import normalvariate

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..")))

import typecheck; from typecheck import typecheck, optional, with_attr

################################################################################

class Timeout:

    @typecheck
    def __init__(self, timeout: float):
        self._timeout = timeout
        self._lock = Lock()
        self.reset()

    timeout = property(lambda self: self._timeout)
    def _rremain(self):
        with self._lock:
            return max(self._deadline - time(), 0.0)
    remain = property(lambda self: self._rremain())

    @typecheck
    def reset(self, timeout: optional(float) = None):
        with self._lock:
            if timeout is not None:
                self._timeout = timeout
            self._deadline = time() + self._timeout

    def reset_random(self):
        with self._lock:
            random_timeout = normalvariate(self._timeout, self._timeout / 9)
            self._deadline = time() + max(random_timeout, 0.0)

    def _expired(self):
        with self._lock:
            return time() >= self._deadline
    expired = property(lambda self: self._expired())

    _never_set = Event()

    @typecheck
    def wait(self, event: optional(with_attr("wait", "is_set")) = None) -> bool:
        remain = self.remain
        if remain > 0:
            if event is None:
                event = self._never_set
            event.wait(remain)
            return event.is_set()
        else:
            return False

    @typecheck
    def pop(self, queue: with_attr("pop")):
        remain = self.remain
        if remain > 0:
            return queue.pop(remain)
        else:
            return None

################################################################################

if __name__ == "__main__":

    print("self-testing module timeout.py:")

    from threading import Event
    from time import sleep

    from typecheck import InputParameterError
    from expected import expected
    from interlocked_queue import InterlockedQueue

    ###################################

    t = Timeout(2.0)
    assert t.remain > 1.9
    sleep(1.25)
    assert t.remain > 0.5
    assert not t.expired
    sleep(1.25)
    assert t.remain == 0.0
    assert t.expired

    t = Timeout(2.0)
    sleep(1.25)
    assert not t.expired
    t.reset()
    assert t.remain > 1.9
    sleep(1.25)
    assert not t.expired

    with expected(InputParameterError("__init__() has got an incompatible value for timeout: 1")):
        Timeout(1)

    start = time()
    t = Timeout(1.0)
    while not t.expired:
        pass
    assert time() - start >= 1.0

    ###################################

    t = Timeout(0.5)
    sleep(1.0)
    assert t.expired
    t.reset()
    sleep(1.0)
    assert t.expired
    t.reset(1.5)
    sleep(1.0)
    assert not t.expired
    sleep(1.0)
    assert t.expired

    ###################################

    t = Timeout(1.0)
    sleep(1.25)
    assert t.expired
    t.reset_random()
    assert not t.expired
    sleep(2.0)
    assert t.expired

    ###################################

    t = Timeout(1.0)
    e = Event()
    assert not t.wait(e) and t.expired
    e.set()
    assert not t.wait(e)

    t = Timeout(1.0)
    assert t.wait(e) and not t.expired

    t = Timeout(0.5)
    assert not t.wait() and t.expired

    ###################################

    ilq = InterlockedQueue()
    t = Timeout(1.0)
    assert t.pop(ilq) is None and t.expired
    ilq.push(1)
    t.reset(0.1)
    assert t.pop(ilq) == 1 and not t.expired

    ###################################

    print("ok")

################################################################################
# EOF
