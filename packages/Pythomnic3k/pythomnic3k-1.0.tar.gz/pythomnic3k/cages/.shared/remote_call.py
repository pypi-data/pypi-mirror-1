#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module is invoked by the module loader when it is processing RPC syntax
#
# pmnc("target_cage").module.method(*args, **kwargs)
#                                                  ^ remote_call.py is called here
#
# If target cage name ends with ":retry" then the call is enqueued through
# the persistent state, otherwise a synchronous RPC call is performed.
# If target cage is just ":retry" then a call to this cage itself is enqueued.
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "execute", "accept", "transmit", "self_test_loopback",
            "self_test_async_local_1", "self_test_async_local_2" ]

###############################################################################

import time; from time import time

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import typecheck; from typecheck import optional, by_regex
import interlocked_queue; from interlocked_queue import InterlockedQueue

###############################################################################
# this method is called by the module loader to handle RPC call
# pmnc("target_cage", **options).module.method(*args, **kwargs)

def execute(target_cage, module, method, args, kwargs, **options):

    if target_cage.endswith(":retry"): # asynchronous retried call

        # execution of asynchronous calls is done through
        # a special resource "pmnc" of protocol "retry"

        xa = pmnc.transaction.create()
        xa.pmnc(target_cage, **options).\
            __getattr__(module).__getattr__(method)(*args, **kwargs)
        return xa.execute()[0]

    else:

        # execution of synchronous RPC calls to a cage foo is done through
        # a separate thread pool rpc__foo, as though each target cage was
        # a separate resource; this is beneficial because it gives an
        # effective mechanism of protecting both this cage from hanging
        # and the other cage from becoming overwhelmed

        xa = pmnc.transaction.create()
        xa.__getattr__("rpc__{0:s}".format(target_cage))(**options).\
           __getattr__(module).__getattr__(method)(*args, **kwargs)
        response = xa.execute()[0]

        # the returned result is a dict which contains either
        # "result" or "exception" received from the other side

        if "exception" in response:
            raise Exception(response["exception"])
        else:
            return response["result"]

###############################################################################
# this method is called from protocol_retry to deliver a retried call to another cage,
# it is itself executed in a retried call and is therefore retried again and again

def transmit(target_cage: str, module: str, method: str, args: tuple, kwargs: dict):

    # the actual transmission is still done through synchronous RPC

    retry = pmnc.request.parameters["retry"]
    source_cage_id = retry["id"]
    target_cage_id = pmnc(target_cage).remote_call.accept(module, method, args, kwargs,
                                                          source_cage_id = source_cage_id,
                                                          retry_deadline = retry["deadline"])

    pmnc.log.info("retried remote call {0:s}.{1:s}.{2:s}() as {3:s} has been "
                  "accepted by cage {0:s} as {4:s}".\
                  format(target_cage, module, method, source_cage_id, target_cage_id))

###############################################################################
# this method accepts incoming retried calls to this cage from other cages
# initiated in transmit above

def accept(module: str, method: str, args: tuple, kwargs: dict, *,
           source_cage_id: by_regex("^RT-[0-9]{14}-[0-9A-F]{12}$"),
           retry_deadline: optional(int), **unused):

    # note that the original unique id of the retried call is used
    # to prevent duplicate invocations and the deadline is also inherited

    if retry_deadline is not None:
        expires_in = max(retry_deadline - time(), 0.0)
    else:
        expires_in = None

    return pmnc(":retry", id = source_cage_id, expires_in = expires_in).\
            __getattr__(module).__getattr__(method)(*args, **kwargs)

###############################################################################

def self_test_loopback(*args, **kwargs):

    if pmnc.request.self_test != __name__:
        raise Exception("invalid access to self-test code")

    if "fail" in kwargs:
        class TestException(Exception): pass
        raise TestException(kwargs["fail"])

    return (args, kwargs, pmnc.request.to_dict())

_self_test_async_local_1_queue = InterlockedQueue()

def self_test_async_local_1(*args, **kwargs):

    if pmnc.request.self_test != __name__:
        raise Exception("invalid access to self-test code")

    retry_id = pmnc(":retry", id = kwargs.get("id2")).__getattr__(__name__).self_test_async_local_2(*args, **kwargs)
    _self_test_async_local_1_queue.push((args, kwargs, pmnc.request.to_dict(), retry_id))

_self_test_async_local_2_queue = InterlockedQueue()

def self_test_async_local_2(*args, **kwargs):

    if pmnc.request.self_test != __name__:
        raise Exception("invalid access to self-test code")

    _self_test_async_local_2_queue.push((args, kwargs, pmnc.request.to_dict()))

###############################################################################

def self_test():

    from time import sleep
    from expected import expected
    from pmnc.request import fake_request

    ###################################

    def start_rpc_interface():
        config = pmnc.config_interface_rpc.copy()
        ifc = pmnc.interface.create("rpc", **config)
        ifc._ad_periods = (1.0, 1.0)
        ifc._cage_name = "somecage"
        ifc.start()
        return ifc

    def stop_rpc_interface(ifc):
        ifc.cease()
        ifc.stop()

    ###################################

    def test_sync_call_success():

        fake_request(10.0)
        pmnc.request.parameters["PARAM"] = "VALUE"

        rpc_ifc = start_rpc_interface()
        try:

            args, kwargs, request_dict = \
                pmnc("somecage").__getattr__(__name__).self_test_loopback(1, "2", foo = "bar")
            assert args == (1, "2")
            assert kwargs == { "foo": "bar" }
            deadline = request_dict.pop("deadline")
            parameters = request_dict.pop("parameters")
            assert request_dict == { "interface": "rpc", "protocol": "rpc",
                                     "unique_id": pmnc.request.unique_id, }
            assert abs(deadline - time() - pmnc.request.remain) < 0.1
            auth_tokens = parameters.pop("auth_tokens")
            auth_tokens.pop("peer_ip")
            assert auth_tokens == { "encrypted": True, "peer_cn": ".*", "source_cage": ".shared" }
            assert parameters == { "PARAM": "VALUE" }

        finally:
            stop_rpc_interface(rpc_ifc)

        # the other side has gone, discard the pooled RPC resource
        # by calling it again which causes it to fail

        try:
            pmnc("somecage").__getattr__(__name__).self_test_loopback()
        except:
            pass

    test_sync_call_success()

    ###################################

    def test_sync_call_failure():

        fake_request(10.0)

        rpc_ifc = start_rpc_interface()
        try:

            with expected(Exception("TestException(\"test\")")):
                pmnc("somecage").__getattr__(__name__).self_test_loopback(fail = "test")

        finally:
            stop_rpc_interface(rpc_ifc)

    test_sync_call_failure()

    ###################################

    def start_retry_interface():
        config = pmnc.config_interface_retry.copy()
        ifc = pmnc.interface.create("retry", **config)
        ifc._lazy_timeout = 8.0
        ifc.start()
        pmnc.interfaces.set_fake_interface("retry", ifc)
        return ifc

    def stop_retry_interface(ifc):
        pmnc.interfaces.delete_fake_interface("retry")
        ifc.cease()
        ifc.stop()

    ###################################

    def test_async_call_local():

        retry_ifc = start_retry_interface()
        try:

            fake_request(10.0)
            sleep(4.0)
            assert abs(pmnc.request.remain - 6.0) < 0.1 # deadline in 6 seconds
            pmnc.request.parameters["PARAM"] = "VALUE"
            request_start = time()
            retry_id1 = pmnc(":retry").__getattr__(__name__).self_test_async_local_1(1, "2", foo = "bar")

            # the first async call

            args, kwargs, request_dict, retry_id2 = _self_test_async_local_1_queue.pop(3.0)
            assert args == (1, "2")
            assert kwargs == { "foo": "bar" }
            assert retry_id2 != retry_id1
            deadline = request_dict.pop("deadline")
            assert deadline - request_start > 9.0 # which means that async request had its own deadline
            retry = request_dict["parameters"].pop("retry")
            start = retry.pop("start")
            assert abs(start - int(request_start)) in (0, 1)
            assert retry == { "attempt": 1, "id": retry_id1, "deadline": None }
            assert request_dict == { "interface": "-", "protocol": "-", "unique_id": pmnc.request.unique_id,
                                     "parameters": { "auth_tokens": {}, "PARAM": "VALUE" } }

            # the second async call, initiated from within the first one

            args, kwargs, request_dict = _self_test_async_local_2_queue.pop(3.0)
            assert args == (1, "2")
            assert kwargs == { "foo": "bar" }
            deadline = request_dict.pop("deadline")
            retry = request_dict["parameters"].pop("retry")
            start = retry.pop("start")
            assert retry == { "attempt": 1, "id": retry_id2, "deadline": None }
            assert request_dict == { "interface": "-", "protocol": "-", "unique_id": pmnc.request.unique_id, # note that request id is the same
                                     "parameters": { "auth_tokens": {}, "PARAM": "VALUE" } }

        finally:
            stop_retry_interface(retry_ifc)

    test_async_call_local()

    ###################################

    def test_async_call_local_with_id():

        retry_ifc = start_retry_interface()
        try:

            fake_request(10.0)
            retry_id1 = pmnc(":retry", id = "ABC123", expires_in = 10.0).\
                        __getattr__(__name__).self_test_async_local_1(id2 = "DEF456")

            # there is no observable difference in behaviour, it is all hidden
            # in protocol_retry, therefore we simply pop the queues

            _self_test_async_local_1_queue.pop(3.0)
            _self_test_async_local_2_queue.pop(3.0)

            # the log should contain decorated filtered id like this:
            # has enqueued retried local call remote_call.self_test_async_local_2(RT-456:DEF456) as RT-789
            #                                                                     ^^^^^^^^^^^^^

        finally:
            stop_retry_interface(retry_ifc)

    test_async_call_local_with_id()

    ###################################

    def test_accept_expiration():

        retry_ifc = start_retry_interface()
        try:

            fake_request(10.0)
            pmnc.__getattr__(__name__).accept("module_never_existed", "method_never_existed", (), {},
                                              source_cage_id = "RT-12345678901234-0123456789AB",
                                              retry_deadline = int(time() + 5.0), future_extension = "not used")

            sleep(40.0) # allow for a retry and cancel

            # again, there is no observable behaviour, the log should contain

            # request RQ-123 has enqueued retried local call module_never_existed.method_never_existed(RT-12345678901234-0123456789AB) as ...
            # ...                                                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # retried local call module_never_existed.method_never_existed(RT-12345678901234-0123456789AB) as ... has expired
            #                                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^         ^^^^^^^^^^^

        finally:
            stop_retry_interface(retry_ifc)

    test_accept_expiration()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
