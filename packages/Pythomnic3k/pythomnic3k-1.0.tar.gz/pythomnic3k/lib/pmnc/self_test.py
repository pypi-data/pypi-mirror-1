#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements testing facility for Pythomnic3k application modules.
# Whenever an application module containing
#
# if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()
#
# runs, this module manages to copy all the files of the current cage to a
# temporary directory, start the copy and invoke the tested module's method
# self_test. Application module code can tell a self-test run from a regular
# run by value of pmnc.request.self_test attribute. If not None, this attribute
# contains the name of the module being tested.
#
# There is an important difference in configuration files behaviour, which
# can be easily observed by examining any configuration file. During a test
# run access to a configuration file requires that the file contains a separate
# section with overridden configuration settings, for example:
#
# config = \
# {
# "server_address": ("real_server", 1234),
# "encoding": "win1251",
# "timeout": 10.0,
# }
#
# self_test_config = \ <- without this section self-test access will fail
# {
# "server_address": ("test_server", 1234), <- only some settings are overriden
# }
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
################################################################################

__all__ = [ "self_test" ]

###############################################################################

import tempfile; from tempfile import mkdtemp
import os; from os import path as os_path, mkdir, listdir, rmdir, remove, chmod
import shutil; from shutil import copyfile, copytree, rmtree
import threading; from threading import Lock, current_thread
import time; from time import time, localtime, strftime, sleep
import stat; from stat import S_IWRITE

import os; import sys
main_module_dir = os_path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
main_module_name = os_path.basename(sys.modules["__main__"].__file__)
assert main_module_name.lower().endswith(".py")
main_module_name = main_module_name[:-3]

if __name__ == "__main__": # add pythomnic/lib to sys.path
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..")))

import exc_string; from exc_string import exc_string
import pmnc.module_loader; from pmnc.module_loader import ModuleLoader
import pmnc.request; from pmnc.request import Request, fake_request
import typecheck; from typecheck import by_regex, optional, tuple_of

###############################################################################

node_name = "self_test"
cage_name = os_path.basename(main_module_dir)

###############################################################################

def non_recursive_copy(source_dir, target_dir, mask):

    if not os_path.isdir(source_dir):
        return

    mkdir(target_dir)
    matching_file = by_regex("^{0:s}$".format(mask))

    for f in listdir(source_dir):
        if matching_file(f.lower()):
            sf = os_path.join(source_dir, f)
            tf = os_path.join(target_dir, f)
            if os_path.isfile(sf):
                copyfile(sf, tf)

###############################################################################

def cage_files_copy(source_cage_dir, target_cage_dir):

    source_dir = source_cage_dir
    target_dir = target_cage_dir
    non_recursive_copy(source_cage_dir, target_cage_dir, "[A-Za-z0-9_-]+\\.py")

    source_dir = os_path.join(source_cage_dir, "ssl_keys")
    target_dir = os_path.join(target_cage_dir, "ssl_keys")
    non_recursive_copy(source_dir, target_dir, "[A-Za-z0-9_-]+\\.pem")

###############################################################################

def create_temp_cage_copy(*, required_dirs):

    test_cages_dir = mkdtemp()

    real_cage_dir = main_module_dir
    test_cage_dir = os_path.join(test_cages_dir, cage_name)
    cage_files_copy(real_cage_dir, test_cage_dir)

    for required_dir in required_dirs:
        real_required_dir = os_path.join(real_cage_dir, required_dir)
        test_required_dir = os_path.join(test_cage_dir, required_dir)
        copytree(real_required_dir, test_required_dir)

    if cage_name != ".shared":

        real_cage_dir = os_path.normpath(os_path.join(real_cage_dir, "..", ".shared"))
        test_cage_dir = os_path.join(test_cages_dir, ".shared")
        cage_files_copy(real_cage_dir, test_cage_dir)

    return test_cages_dir

###############################################################################

def try_remove_dir(s):

    for i in range(3):
        try:
            rmdir(s)
        except:
            sleep(1.0)
        else:
            break

###############################################################################

def remove_temp_cage_copy(test_cages_dir):

    sleep(3.0) # this allows dust to settle

    def retry_remove(func, path, exc): # this allows to remove a read-only file
        try:
            chmod(path, S_IWRITE)
            func(path)
        except:
            pass

    for i in range(3):
        try:
            if os_path.isdir(test_cages_dir):
                rmtree(test_cages_dir, onerror = retry_remove)
        except:
            sleep(1.0)
    else:
        if os_path.isdir(test_cages_dir):
            rmtree(test_cages_dir, onerror = retry_remove)

###############################################################################

log_priorities = { 1: "ERR", 2: "MSG", 3: "WRN", 4: "LOG", 5: "INF", 6: "DBG" }
log_lock = Lock()

def log(s, *, priority = 2):
    t = time(); lt = localtime(t)
    c = priority < 2 and "*" or " "
    s = "{0:s}.{1:02d}{2:s}{3:s}{4:s}[{5:s}] {6}".format(strftime("%H:%M:%S", lt), int(t * 100) % 100,
                                                         c, log_priorities.get(priority, "???"), c,
                                                         current_thread().name, s)
    with log_lock:
        print(s)

###############################################################################

def start_pmnc(test_cages_dir):

    test_cage_dir = os_path.join(test_cages_dir, cage_name)

    Request._self_test = main_module_name
    fake_request()

    pmnc = ModuleLoader(node_name, cage_name, test_cage_dir, log, 6)
    try:
        pmnc.startup.start()
    except:
        pmnc.startup.stop()
        raise
    else:
        return pmnc

###############################################################################

def stop_pmnc(pmnc):

    pmnc.startup.stop()

###############################################################################

def run(*, required_dirs: optional(tuple_of(str)) = ()):

    current_thread().name = "self_test"

    log("***** STARTING SELF-TEST FOR MODULE {0:s} *****".format(main_module_name.upper()))
    test_cages_dir = create_temp_cage_copy(required_dirs = required_dirs)
    try:
        pmnc = start_pmnc(test_cages_dir)
        try:
            try:
                assert pmnc.request.self_test == main_module_name
                pmnc.__getattr__(main_module_name).self_test()
            except:
                log("***** FAILURE: {1:s}".format(main_module_name, exc_string()))
            else:
                log("***** SUCCESS, BUT EXAMINE THE LOG FOR UNEXPECTED ERRORS *****")
        finally:
            stop_pmnc(pmnc)
    finally:
        remove_temp_cage_copy(test_cages_dir)

################################################################################
# EOF
