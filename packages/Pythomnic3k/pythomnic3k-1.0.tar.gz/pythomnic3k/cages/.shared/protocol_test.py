#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements an empty resource which is used by module transaction.py
# for self-testing. For the same reason there exist the file config_resource_test.py.
#
# Sample resource usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.test.execute(*args, **kwargs)
# config, args, kwargs, request_dict = xa.execute()[0]
#
# xa = pmnc.transaction.create(fail_execute = "error message")
# xa.test.execute(*args, **kwargs)
# xa.execute() # fails with "error message"
#
# xa = pmnc.transaction.create(delay_execute = 3.0)
# xa.test.execute(*args, **kwargs)
# xa.execute() # sleeps for 3 seconds
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Resource" ]

###############################################################################

import time; from time import sleep

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import typecheck; from typecheck import typecheck
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource

###############################################################################

class Resource(TransactionalResource): # "test" resource

    @typecheck
    def __init__(self, name: str, **config):
        TransactionalResource.__init__(self, name)
        self._config = config

    def connect(self):
        TransactionalResource.connect(self)

    # this method throws or delays if so is specified in transaction options

    def _fail_delay(self, suffix):
        value = self.transaction_options.get("fail_{0:s}".format(suffix))
        if value:
            raise Exception(value)
        value = self.transaction_options.get("delay_{0:s}".format(suffix))
        if value:
            sleep(value)

    def execute(self, *args, **kwargs):
        self._fail_delay("execute")
        return dict(config = self._config, args = args, kwargs = kwargs,
                    xid = self.xid, transaction_options = self.transaction_options,
                    resource_args = self.resource_args, resource_kwargs = self.resource_kwargs,
                    request = pmnc.request.to_dict())

    def commit(self):
        self._fail_delay("commit")

    def rollback(self):
        self._fail_delay("rollback")

    def disconnect(self):
        TransactionalResource.disconnect(self)

###############################################################################
# EOF