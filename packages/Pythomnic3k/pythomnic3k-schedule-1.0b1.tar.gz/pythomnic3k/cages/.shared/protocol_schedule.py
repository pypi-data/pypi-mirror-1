#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
###############################################################################
#
# This module contains an implementation of schedule interface (periodic
# request execution at specified times).
#
# Note that this interface does not wait for the requests it initiates.
#
# Sample schedule interface configuration (config_interface_schedule_1.py):
#
# config = dict \
# (
# protocol = "schedule",     # meta
# format = "%H:%M",          # schedule (argument to strftime)
# match = "12:30",           # schedule (regular expression to match)
# )
#
# Sample processing module (interface_schedule_1.py):
#
# def process_request(request, response):
#     invocation_time = request["invocation_time"]
#     pmnc.log("invoked at {0:s}".format(invocation_time.strftime("%H:%M")))
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface" ]

###############################################################################

import threading; from threading import current_thread
import datetime; from datetime import datetime
import time; from time import time, mktime, sleep
import math; from math import modf

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck, by_regex
import pmnc.threads; from pmnc.threads import HeavyThread

###############################################################################

class Interface: # schedule interface

    @typecheck
    def __init__(self, name: str, *,
                 format: str,
                 match: str,
                 **kwargs): # this kwargs allows for extra application-specific
                            # settings in config_interface_schedule_X.py
        self._name = name
        self._format = format
        self._match = by_regex("(?:{0:s})".format(match))
        self._last_tick = self._get_current_tick()

        if pmnc.request.self_test == __name__: # self-test harness
            self._output_queue = kwargs.pop("__output_queue")
            self._output_value = kwargs.pop("__output_value")

    name = property(lambda self: self._name)

    ###################################

    def _get_current_tick(self):
        return int(mktime(datetime.now().timetuple()))

    ###################################

    def start(self):
        self._scheduler = HeavyThread(target = self._scheduler_proc,
                                      name = "{0:s}:sch".format(self._name))
        self._scheduler.start()

    def cease(self):
        self._scheduler.stop()

    def stop(self):
        pass

    ###################################

    def _scheduler_proc(self):

        while not current_thread().stopped(1.1 - modf(time())[0]):
            try:

                current_tick = self._get_current_tick()
                try:
                    for tick in range(self._last_tick + 1, current_tick + 1):
                        if self._match(datetime.fromtimestamp(tick).strftime(self._format)):
                            try:
                                self._fire_request(tick)
                            except:
                                pmnc.log.error(exc_string()) # log and ignore
                finally:
                    self._last_tick = current_tick

            except:
                pmnc.log.error(exc_string()) # log and ignore

    ###################################

    def _fire_request(self, tick): # note that this interface does not wait for its requests to complete

        request = pmnc.interfaces.begin_request(timeout = pmnc.config_interfaces.get("request_timeout"),
                                                interface = self._name,
                                                protocol = "schedule",
                                                parameters = {})

        pmnc.performance.event("interface.{0:s}.request_rate".format(self._name))

        pmnc.log.info("interface {0:s} introduces request {1:s}, deadline in {2:.01f} second(s)".\
                      format(self._name, request.unique_id, request.remain))

        pmnc.interfaces.enqueue(request, self.wu_execute_request, (tick, ))

    ###################################

    def wu_execute_request(self, tick):

        try:

            try:

                try:

                    # see for how long the request was on the execution queue up to this moment
                    # and whether it has expired in the meantime, if it did there is no reason
                    # to proceed and we simply bail out

                    if pmnc.request.expired:
                        raise Exception("processing of request {0:s} was late by {1:.01f} second(s)".\
                                        format(pmnc.request.unique_id, pmnc.request.expired_for))

                    start = pmnc.request.elapsed
                    try:

                        try:


                            pending_ms = int(pmnc.request.elapsed * 1000)
                            pmnc.performance.sample("interface.{0:s}.pending_time".\
                                                    format(self._name), pending_ms)

                            request = dict(invocation_time = datetime.fromtimestamp(tick))
                            response = dict()

                            with pmnc.performance.timing("interface.{0:s}.processing_time".\
                                                         format(self._name)):

                                if pmnc.request.self_test == __name__: # self-test harness

                                    self._output_queue.push(eval(self._output_value))

                                else: # default behaviour is to invoke the application handler

                                    handler_module_name = "interface_{0:s}".format(self._name)
                                    pmnc.__getattr__(handler_module_name).process_request(request, response)

                        except:
                            pmnc.log.error("schedule processing has failed: {0:s}".format(exc_string()))
                            raise
                        else:
                            pmnc.log.info("schedule processing has succeeded")

                    finally:
                        elapsed_sec = pmnc.request.elapsed - start
                        elapsed_ms = int(elapsed_sec * 1000)

                except:
                    pmnc.log.info("request {0:s} has delivered a (failure) response in {1:.01f} "
                                  "second(s)".format(pmnc.request.unique_id, elapsed_sec))
                    raise
                else:
                    pmnc.log.info("request {0:s} has delivered a (success) response in {1:.01f} "
                                  "second(s)".format(pmnc.request.unique_id, elapsed_sec))

            except:
                pmnc.performance.sample("interface.{0:s}.response_time.failure".\
                                        format(self._name), elapsed_ms)
                pmnc.performance.event("interface.{0:s}.response_rate.failure".\
                                       format(self._name))
            else:
                pmnc.performance.sample("interface.{0:s}.response_time.success".\
                                        format(self._name), elapsed_ms)
                pmnc.performance.event("interface.{0:s}.response_rate.success".\
                                       format(self._name))

        finally:
            pmnc.interfaces.end_request(pmnc.request)

###############################################################################

def self_test():

    from interlocked_queue import InterlockedQueue

    ###################################

    def start_interface(output_queue, output_value):
        config = pmnc.config_interface_schedule_1.copy()
        ifc = pmnc.interface.create("schedule_1", __output_queue = output_queue, __output_value = output_value, **config)
        ifc.start()
        return ifc

    ###################################

    def test_interface_success():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue, "sleep(0.1) or 'ok'")
        try:
            assert output_queue.pop(4.0) == "ok"
            assert output_queue.pop(1.0) is None
            assert output_queue.pop(3.0) == "ok"
            assert output_queue.pop(1.0) is None
            assert output_queue.pop(3.0) == "ok"
        finally:
            ifc.cease(); ifc.stop()

    test_interface_success()

    ###################################

    def test_interface_failure():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue, "sleep(0.1) or not_defined")
        try:
            assert output_queue.pop(4.0) is None
        finally:
            ifc.cease(); ifc.stop()

    test_interface_failure()

    ###################################

    def test_interface_no_wait():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue, "sleep(5.0) or tick")
        try:
            t1 = output_queue.pop(9.0)
            t2 = output_queue.pop(6.0)
            t3 = output_queue.pop(6.0)
        finally:
            ifc.cease(); ifc.stop()

        assert (t2 - t1) == (t3 - t2) == 3

    test_interface_no_wait()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
