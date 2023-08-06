#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module transmits notification messages to the health_monitor cage.
# Last few are kept locally and are accessible via interface_performance.
#
# Sample:
# pmnc.notify.info("this will appear in health_monitor's log")
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
################################################################################

__all__ = [ "info", "warning", "error", "alert", "extract" ]

################################################################################

import time; from time import time
import threading; from threading import Lock

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

################################################################################

def info(message: str):
    _notify("INFO", message)

def warning(message: str):
    _notify("WARNING", message)

def error(message: str):
    _notify("ERROR", message)

def alert(message: str):
    _notify("ALERT", message)

################################################################################

rpc_interfaces_available = None
notifications = []              # technically, this is a module-level state, but
notifications_lock = Lock()     # expendable, therefore the module is reloadable

def _notify(level, message):

    timestamp = int(time())

    pmnc.log.message("[{0:s}] {1:s}".format(level, message))
    with notifications_lock:
        notifications.append(dict(timestamp = timestamp, level = level, message = message))
        while len(notifications) > 100:
            notifications.pop(0)

    if __cage__ != "health_monitor":
        global rpc_interfaces_available
        if rpc_interfaces_available is None:
            rpc_interfaces_available = pmnc.interfaces.get_interface("rpc") is not None and \
                                       pmnc.interfaces.get_interface("retry") is not None
        if rpc_interfaces_available:
            pmnc("health_monitor:retry").\
                health_monitor_event.notify(timestamp, __node__, __cage__, level, message)

###############################################################################

def extract():
    with notifications_lock:
        return notifications[:]

###############################################################################

def self_test():

    from pmnc.request import fake_request

    ###################################

    def test_notify():

        fake_request(10.0)

        pmnc.notify.info("info")
        pmnc.notify.warning("warning")
        pmnc.notify.error("error")
        pmnc.notify.alert("alert")

        assert len(notifications) == 4
        extracted_notifications = pmnc.notify.extract()
        assert extracted_notifications is not notifications

        assert [ (type(d["timestamp"]), d["level"], d["message"]) for d in extracted_notifications ] == \
               [ (int, "INFO", "info"), (int, "WARNING", "warning"), (int, "ERROR", "error"), (int, "ALERT", "alert") ]

    test_notify()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF