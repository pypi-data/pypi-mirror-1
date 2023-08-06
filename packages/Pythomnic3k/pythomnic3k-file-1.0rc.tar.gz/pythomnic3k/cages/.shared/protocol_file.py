#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
###############################################################################
#
# This module contains an implementation of file interface (periodic polling
# of a shared directory) and resource (writing files to a shared directory).
#
# Note that the interface processes the files in alphabetical order.
# If more files appear during one pass, they will only be picked up at another.
#
# Note that with resource the files are saved to temporary files first and
# only renamed at commit. It would be polite to provide input files for the
# interface in the same fashion, otherwise it could pick up an incomplete file.
#
# Sample file interface configuration (config_interface_file_1.py):
#
# config = dict \
# (
# protocol = "file",                       # meta
# source_directory = "/tmp",               # file
# filename_regex = "[A-Za-z0-9_]+\\.msg",  # file
# interval = 10.0,                         # file
# )
#
# Sample processing module (interface_file_1.py):
#
# def process_request(request, response):
#   file_name = request["file_name"]
#   with open(file_name, "rb") as f:
#     data = f.read()
#
# Sample file resource configuration (config_resource_file_1.py)
#
# config = dict \
# (
# protocol = "file",           # meta
# target_directory = "/tmp",   # file (optional)
# temp_directory = None,       # file (optional, separate directory for temporary files)
# temp_extension = "tmp",      # file
# )
#
# Sample resource usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.file_1.write("foo.msg", b"data")
# assert xa.execute()[0] == "/tmp/foo.msg"
#
# xa = pmnc.transaction.create()
# xa.file_1.write("supports/subdirector.ies", b"too")
# assert xa.execute()[0] == "/tmp/supports/subdirector.ies"
#
# Pythomnic3k project
# (c) 2005-2010, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource", "retry_remove" ]

###############################################################################

import os; from os import path as os_path, fdopen, remove, rename, makedirs, fsync
import tempfile; from tempfile import mkstemp
import threading; from threading import current_thread
import time; from time import sleep

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck, optional, by_regex, nothing
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource
import pmnc.threads; from pmnc.threads import HeavyThread

###############################################################################
# this utility method compensates for sporadic deletion errors in loaded
# filesystem by repeating the attempt, exported because it is useful

def retry_remove(filename: str, timeout: optional(float) = None):
    try:
        remove(filename)
    except:
        pmnc.log.warning(exc_string())
        if timeout is None: timeout = pmnc.request.remain
        sleep(min(timeout, 2.0)) # retry in a little while, and
        remove(filename)         # if it fails again it fails

###############################################################################

class Interface: # file-loading interface

    @typecheck
    def __init__(self, name: str, *,
                 source_directory: os_path.isdir,
                 filename_regex: str,
                 interval: float,
                 **kwargs): # this kwargs allows for extra application-specific
                            # settings in config_interface_file_X.py
        self._name = name
        self._source_directory = source_directory
        self._valid_filename = by_regex("^{0:s}$".format(filename_regex))
        self._interval = interval
        self._removed_files = set()

        if pmnc.request.self_test == __name__: # self-test harness
            self._output_queue = kwargs.pop("__output_queue")

    name = property(lambda self: self._name)

    ###################################

    def start(self):
        self._spooler = HeavyThread(target = self._spooler_proc,
                                    name = "{0:s}:spool".format(self._name))
        self._spooler.start()

    def cease(self):
        self._spooler.stop()

    def stop(self):
        pass

    ###################################

    def _check_removed_files(self):
        self._removed_files = set(file_name for file_name in self._removed_files
                                  if os_path.isfile(os_path.join(self._source_directory, file_name)))

    ###################################

    class SpooledFile:

        def __init__(self, source_directory, file_name, valid_filename):
            self._file_name = file_name
            self._full_file_name = os_path.join(source_directory, file_name)
            self._valid = valid_filename(file_name)

        name = property(lambda self: self._file_name)
        full_name = property(lambda self: self._full_file_name)
        valid = property(lambda self: self._valid)
        exists = property(lambda self: os_path.isfile(self._full_file_name))

    ###################################

    def _spooler_proc(self):

        spool_interval = self._interval

        while not current_thread().stopped(spool_interval):
            try:

                spooled_files = [ spooled_file for spooled_file
                                  in map(lambda file_name: self.SpooledFile(self._source_directory, file_name,
                                                                            self._valid_filename),
                                         os.listdir(self._source_directory))
                                  if spooled_file.valid and spooled_file.exists and
                                     spooled_file.name not in self._removed_files ]

                if spooled_files:
                    spooled_files.sort(key = lambda spooled_file: spooled_file.name)
                    for spooled_file in spooled_files:
                        if current_thread().stopped():
                            break
                        elif not self._process_file(spooled_file):
                            spool_interval = self._interval
                            break
                    else:
                        spool_interval = 0.0
                else:
                    spool_interval = self._interval

                self._check_removed_files()

            except:
                pmnc.log.error(exc_string())
                spool_interval = self._interval

    ###################################

    def _process_file(self, spooled_file):

        request_parameters = dict(auth_tokens = dict())
        request = pmnc.interfaces.begin_request(timeout = pmnc.config_interfaces.get("request_timeout"),
                                                interface = self._name,
                                                protocol = "file",
                                                parameters = request_parameters)
        try:

            pmnc.log.info("directory {0:s} via interface {1:s} introduces request {2:s} for "
                          "processing file {3:s}, deadline in {4:.01f} second(s)".\
                          format(self._source_directory, self._name, request.unique_id,
                                 spooled_file.name, request.remain))

            pmnc.performance.event("interface.{0:s}.request_rate".format(self._name))
            try:

                try:

                    try:

                        try:

                            # schedule file processing and wait for its completion

                            pmnc.interfaces.enqueue(request, self.wu_process_file, (spooled_file, )).wait()

                            # if the file still exists, attempt to remove it,
                            # and if it couldn't be removed remember its name

                            self._removed_files.add(spooled_file.name)
                            try:
                                if spooled_file.exists:
                                    retry_remove(spooled_file.full_name, request.remain)
                            except:
                                pmnc.log.warning(exc_string()) # log and ignore
                            else:
                                self._removed_files.remove(spooled_file.name)

                        except:
                            pmnc.log.error("processing of file {0:s} has failed: {1:s}".\
                                           format(spooled_file.name, exc_string()))
                            raise
                        else:
                            pmnc.log.info("processing of file {0:s} has succeeded".\
                                          format(spooled_file.name))

                    finally:
                        elapsed_sec = request.elapsed
                        elapsed_ms = int(elapsed_sec * 1000)

                except:
                    pmnc.log.info("request {0:s} has delivered a (failure) response in {1:.01f} "
                                  "second(s)".format(request.unique_id, elapsed_sec))
                    raise
                else:
                    pmnc.log.info("request {0:s} has delivered a (success) response in {1:.01f} "
                                  "second(s)".format(request.unique_id, elapsed_sec))

            except:
                pmnc.performance.sample("interface.{0:s}.response_time.failure".\
                                        format(self._name), elapsed_ms)
                pmnc.performance.event("interface.{0:s}.response_rate.failure".\
                                       format(self._name))
                return False
            else:
                pmnc.performance.sample("interface.{0:s}.response_time.success".\
                                        format(self._name), elapsed_ms)
                pmnc.performance.event("interface.{0:s}.response_rate.success".\
                                       format(self._name))
                return True

        finally:

            # although the request may still be pending for execution,
            # there is need to wait for it any more

            pmnc.interfaces.end_request(request)

    ###################################

    @typecheck
    def wu_process_file(self, spooled_file: SpooledFile):

        # see for how long the request was on the execution queue up to this moment
        # and whether it has expired in the meantime, if it did there is no reason
        # to proceed and we simply bail out

        if pmnc.request.expired:
            raise Exception("processing of request {0:s} was late by {1:.01f} second(s)".\
                            format(pmnc.request.unique_id, pmnc.request.expired_for))

        pending_ms = int(pmnc.request.elapsed * 1000)
        pmnc.performance.sample("interface.{0:s}.pending_time".\
                                format(self._name), pending_ms)

        request = dict(file_name = spooled_file.full_name)
        response = dict()

        with pmnc.performance.timing("interface.{0:s}.processing_time".\
                                     format(self._name)):

            if pmnc.request.self_test == __name__: # self-test harness

                with open(spooled_file.full_name, "rb") as f:
                    data = f.read()
                self._output_queue.push(eval(data))

            else: # default behaviour is to invoke the application handler

                handler_module_name = "interface_{0:s}".format(self._name)
                pmnc.__getattr__(handler_module_name).process_request(request, response)

###############################################################################

class Resource(TransactionalResource): # file-saving resource

    @typecheck
    def __init__(self, name: str, *,
                 target_directory: optional(str) = None,
                 temp_directory: optional(str) = None,
                 temp_extension: str):

        TransactionalResource.__init__(self, name)

        self._target_directory = target_directory
        self._temp_directory = temp_directory
        self._temp_suffix = ".{0:s}".format(temp_extension)

    def begin_transaction(self, *args, **kwargs):
        TransactionalResource.begin_transaction(self, *args, **kwargs)
        self._temp_filename = None

    @typecheck
    def write(self, target_filename: str, data_b: bytes) -> str:

        # determine the location of the target file
        # and create the target directory if necessary

        if self._target_directory:
            target_filename = os_path.join(self._target_directory, target_filename)
        self._target_filename = os_path.normpath(target_filename)

        target_directory = os_path.dirname(self._target_filename)
        if not os_path.isdir(target_directory):
            self._create_directory(target_directory)

        # determine the location of temporary files
        # and create the temporary directory if necessary

        temp_directory = os_path.normpath(self._temp_directory or target_directory)
        if not os_path.isdir(temp_directory):
            self._create_directory(temp_directory)

        # write data to a temporary file and make sure
        # it has been persistently stored to disk

        h, self._temp_filename = mkstemp(dir = temp_directory, suffix = self._temp_suffix)

        pmnc.log.info("writing {0:d} byte(s) to a temporary file {1:s}".\
                      format(len(data_b), self._temp_filename))

        with fdopen(h, "wb") as f:
            if pmnc.request.self_test == __name__: # self-test harness
                data_b = eval(data_b)
            f.write(data_b); f.flush(); fsync(f.fileno())

        # if the target file already exists, we are unable to commit
        # the transaction anyway, therefore fail to cause rollback

        if os_path.exists(self._target_filename):
            raise Exception("file {0:s} already exists".\
                            format(self._target_filename))
        else:
            return self._target_filename

    # commit can fail unexpectedly, for example if the target file
    # appears which did not exist as per check in write(), and there
    # is nothing we can do with it, however the temp file still remains

    def commit(self):
        try:
            rename(self._temp_filename, self._target_filename)
        except:
            pmnc.log.error("failed to rename temporary file {0:s} to {1:s}".\
                           format(self._temp_filename, self._target_filename))
            raise # causes "unexpected commit failure"
        else:
            pmnc.log.info("temporary file {0:s} has been renamed to {1:s}".\
                           format(self._temp_filename, self._target_filename))

    def rollback(self):
        if self._temp_filename:
            try:
                retry_remove(self._temp_filename)
            except:
                pmnc.log.error("failed to remove temporary file {0:s}".\
                               format(self._temp_filename))
                raise
            else:
                pmnc.log.info("temporary file {0:s} has been removed".\
                              format(self._temp_filename))

    # this utility method ensures the directory exists,
    # directory creation attempt is exclusively interlocked

    def _create_directory(self, directory):
        makedirs_lock = pmnc.shared_locks.get("{0:s}.Resource._create_directory".\
                                              format(__name__))
        pmnc.request.acquire(makedirs_lock)
        try:
            if not os_path.isdir(directory):
                makedirs(directory)
        finally:
            makedirs_lock.release()

###############################################################################

def self_test():

    from os import urandom, rmdir
    from binascii import b2a_hex
    from pmnc.request import fake_request
    from expected import expected
    from typecheck import InputParameterError
    from interlocked_queue import InterlockedQueue
    from random import shuffle

    ###################################

    def random_filename():
        return b2a_hex(urandom(4)).decode("ascii")

    write_prefix = random_filename()

    def write_file(filename, data):
        filename = os_path.join(pmnc.config_interface_file_1.get("source_directory"),
                                write_prefix + filename)
        with open(filename, "wb") as f:
            f.write(data)
        return filename

    ###################################

    def start_interface(output_queue = None):
        config = pmnc.config_interface_file_1.copy()
        config.update(filename_regex = write_prefix + "[0-9a-f]{8}\\.msg")
        ifc = pmnc.interface.create("file_1", __output_queue = output_queue, **config)
        ifc.start()
        return ifc

    ###################################

    def test_interface_start_stop():

        ifc = start_interface()
        try:
            sleep(3.0)
        finally:
            ifc.cease(); ifc.stop()

    test_interface_start_stop()

    ###################################

    def test_interface_success():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue)
        try:

            assert output_queue.pop(3.0) is None
            file_name = write_file(random_filename() + ".msg", b"request")
            assert os_path.isfile(file_name)
            assert output_queue.pop(3.0) == { "file_name": file_name }
            sleep(3.0); assert not os_path.exists(file_name)
            assert output_queue.pop(3.0) is None

        finally:
            ifc.cease(); ifc.stop()

    test_interface_success()

    ###################################

    def test_interface_skip():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue)
        try:

            assert output_queue.pop(3.0) is None
            file_name = write_file(random_filename() + ".tmp", b"request")
            assert os_path.isfile(file_name)
            assert output_queue.pop(3.0) is None
            assert os_path.isfile(file_name)
            retry_remove(file_name, 2.0)

        finally:
            ifc.cease(); ifc.stop()

    test_interface_skip()

    ###################################

    def test_interface_failure():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue)
        try:

            assert output_queue.pop(3.0) is None
            file_name = write_file(random_filename() + ".msg", b"not_defined")
            assert os_path.isfile(file_name)
            assert output_queue.pop(3.0) is None
            assert os_path.isfile(file_name)
            retry_remove(file_name, 2.0)

        finally:
            ifc.cease(); ifc.stop()

    test_interface_failure()

    ###################################

    def test_interface_timeout():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue)
        try:

            assert output_queue.pop(3.0) is None
            file_name = write_file(random_filename() + ".msg", b"sleep(12.0) or request")
            assert os_path.isfile(file_name)
            assert output_queue.pop(3.0) is None
            assert os_path.isfile(file_name)
            assert output_queue.pop(13.0) == { "file_name": file_name }
            assert os_path.isfile(file_name)
            retry_remove(file_name, 2.0)

        finally:
            ifc.cease(); ifc.stop()

    test_interface_timeout()

    ###################################

    def test_interface_ordering():

        output_queue = InterlockedQueue()

        file_names = [ "{0:08d}.msg".format(i) for i in range(100) ]
        shuffle(file_names)

        for file_name in file_names:
            write_file(file_name, b"sleep(0.1) or request")

        ifc = start_interface(output_queue)
        try:

            for i in range(100):
                assert output_queue.pop(3.0)["file_name"].endswith("{0:08d}.msg".format(i))
                if i % 10 == 9:
                    write_file("{0:08d}.msg".format(i // 10), b"sleep(0.1) or request")

            for i in range(10):
                assert output_queue.pop(3.0)["file_name"].endswith("{0:08d}.msg".format(i))

            assert output_queue.pop(3.0) is None

        finally:
            ifc.cease(); ifc.stop()

    test_interface_ordering()

    ###################################

    def test_interface_remove():

        output_queue = InterlockedQueue()

        ifc = start_interface(output_queue)
        try:

            file_name = write_file(random_filename() + ".msg", b"remove(request['file_name']) or 'removed'")
            assert output_queue.pop(3.0) == "removed"
            assert output_queue.pop(3.0) is None

        finally:
            ifc.cease(); ifc.stop()

    test_interface_remove()

    ###################################

    def test_interface_stuck():

        output_queue = InterlockedQueue()

        global remove
        remove = lambda f: delete_is_not_defined

        ifc = start_interface(output_queue)
        try:

            fn = random_filename() + ".msg"
            file_name = write_file(fn, b"request")
            assert output_queue.pop(3.0) == { "file_name": file_name }
            sleep(3.0); assert os_path.isfile(file_name)
            assert ifc._removed_files == { write_prefix + fn }
            assert output_queue.pop(3.0) is None
            assert os_path.isfile(file_name)
            assert ifc._removed_files == { write_prefix + fn }

            remove = os.remove
            remove(file_name)
            assert output_queue.pop(3.0) is None
            assert not ifc._removed_files

        finally:
            ifc.cease(); ifc.stop()

    test_interface_stuck()

    ###################################

    def target_filename(s):
        return os_path.normpath(os_path.join(pmnc.config_resource_file_1.get("target_directory"), s))

    ###################################

    def test_resource_commit():

        def test_file(fn):

            assert not os_path.isfile(target_filename(fn))
            fake_request(10.0)

            xa = pmnc.transaction.create()
            xa.file_1.write(fn, b"b\"\\x00\"")
            assert xa.execute()[0] == target_filename(fn)

            with open(target_filename(fn), "rb") as f:
                assert f.read() == b"\x00"

            retry_remove(target_filename(fn), 2.0)

        dn = random_filename()
        assert not os_path.isdir(target_filename(dn))
        test_file(os_path.join(dn, random_filename()))
        assert os_path.isdir(target_filename(dn))

        sleep(3.0); rmdir(target_filename(dn))

    test_resource_commit()

    ###################################

    def test_resource_rollback():

        fn = random_filename()
        assert not os_path.isfile(target_filename(fn))

        fake_request(3.0)

        xa = pmnc.transaction.create()
        xa.file_1.write(fn, "should have been bytes")
        with expected(InputParameterError):
            xa.execute()
        assert not os_path.isfile(target_filename(fn))

        fn = random_filename()
        assert not os_path.isfile(target_filename(fn))

        fake_request(3.0)

        xa = pmnc.transaction.create()
        xa.file_1.write(fn, b"b\"should be ok\"")
        xa.execute()
        assert os_path.isfile(target_filename(fn))

        xa = pmnc.transaction.create()
        xa.file_1.write(fn, b"b\"should fail this time\"")
        with expected(Exception):
            xa.execute()
        assert os_path.isfile(target_filename(fn))
        retry_remove(target_filename(fn), 2.0)

        dn = random_filename()
        assert not os_path.isdir(target_filename(dn))
        fn = os_path.join(dn, random_filename())
        assert not os_path.isfile(target_filename(fn))

        fake_request(3.0)

        xa = pmnc.transaction.create()
        xa.file_1.write(fn, b"not_defined")
        with expected(NameError):
            xa.execute()
        assert not os_path.isfile(target_filename(fn))
        assert os_path.isdir(target_filename(dn))

        sleep(3.0); rmdir(target_filename(dn))

    test_resource_rollback()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
