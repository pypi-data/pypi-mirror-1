#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module contains an implementation of XMLRPC interface/resource.
#
# Sample XMLRPC interface configuration (config_interface_xmlrpc_1.py):
#
# config = dict \
# (
# protocol = "xmlrpc",                                       # meta
# listener_address = ("127.0.0.1", 8000),                    # tcp
# max_connections = 100,                                     # tcp
# ssl_key_cert_file = None,                                  # ssl
# ssl_ca_cert_file = None,                                   # ssl
# response_encoding = "windows-1251",                        # http
# original_ip_header_fields = ("X-Forwarded-For", ),         # http
# keep_alive_support = True,                                 # http
# keep_alive_idle_timeout = 120.0,                           # http
# keep_alive_max_requests = 10,                              # http
# )
#
# Sample processing module (interface_xmlrpc_1.py):
#
# def process_request(request, response):
#   module, method = request["method"].split(".")
#   args = request["args"]
#   result = pmnc.__getattr__(module).__getattr__(method)(*args)
#   response["result"] = result
#
# Sample XMLRPC resource configuration (config_resource_xmlrpc_1.py)
#
# config = dict \
# (
# protocol = "xmlrpc",                                       # meta
# server_address = ("127.0.0.1", 8000),                      # tcp
# connect_timeout = 3.0,                                     # tcp
# ssl_key_cert_file = None,                                  # ssl
# ssl_ca_cert_file = None,                                   # ssl
# extra_headers = { "Authorization": "Basic dXNlcjpwYXNz" }, # http
# http_version = "HTTP/1.1",                                 # http
# server_uri = "/xmlrpc",                                    # xmlrpc
# request_encoding = "windows-1251",                         # xmlrpc
# )
#
# Sample resource usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.xmlrpc_1.Module.Method(*args)
# result = xa.execute()[0]
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource", "process_http_request" ]

###############################################################################

import os; from os import path as os_path
import xmlrpc.client; from xmlrpc.client import loads, dumps, Fault

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import typecheck; from typecheck import typecheck, optional, tuple_of, dict_of, callable
import exc_string; from exc_string import exc_string
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource

###############################################################################

class Interface: # XMLRPC interface built on top of HTTP interface

    @typecheck
    def __init__(self, name: str, *,
                 listener_address: (str, int),
                 max_connections: int,
                 ssl_key_cert_file: optional(os_path.isfile),
                 ssl_ca_cert_file: optional(os_path.isfile),
                 response_encoding: str,
                 original_ip_header_fields: tuple_of(str),
                 keep_alive_support: bool,
                 keep_alive_idle_timeout: float,
                 keep_alive_max_requests: int,
                 **kwargs): # this kwargs allows for extra application-specific
                            # settings in config_interface_xmlrpc_X.py

        # create an instance of underlying HTTP interface

        self._http_interface = \
            pmnc.protocol_http.Interface(name,
                                         listener_address = listener_address,
                                         max_connections = max_connections,
                                         ssl_key_cert_file = ssl_key_cert_file,
                                         ssl_ca_cert_file = ssl_ca_cert_file,
                                         response_encoding = response_encoding,
                                         original_ip_header_fields = original_ip_header_fields,
                                         allowed_methods = ("POST", ),
                                         keep_alive_support = keep_alive_support,
                                         keep_alive_idle_timeout = keep_alive_idle_timeout,
                                         keep_alive_max_requests = keep_alive_max_requests)

        # override the default process_http_request method of the created HTTP interface

        self._http_interface.process_http_request = \
            lambda http_request, http_response: \
                pmnc.protocol_xmlrpc.process_http_request(http_request, http_response,
                                                          self.process_xmlrpc_request,
                                                          response_encoding = response_encoding)

    name = property(lambda self: self._http_interface.name)
    listener_address = property(lambda self: self._http_interface.listener_address)

    ###################################

    def start(self):
        self._http_interface.start()

    def cease(self):
        self._http_interface.cease()

    def stop(self):
        self._http_interface.stop()

    ###################################

    @typecheck
    def process_xmlrpc_request(self, xmlrpc_request: dict, xmlrpc_response: dict):

        # default behaviour is to invoke the application handler

        handler_module_name = "interface_{0:s}".format(self.name)
        pmnc.__getattr__(handler_module_name).process_request(xmlrpc_request, xmlrpc_response)

###############################################################################

def process_http_request(http_request: dict, http_response: dict,
                         process_xmlrpc_request: callable, *,
                         response_encoding: str):

    assert http_request["method"] == "POST"
    headers = http_request["headers"]
    content = http_request["content"]

    content_type = headers.get("content-type", "application/octet-stream")
    if not content_type.startswith("text/xml"):
        http_response["status_code"] = 415 # unsupported media type
        return

    # extract xmlrpc request from http request content, the parser
    # will deduce the bytes encoding from the <?xml encoding attribute

    try:
        args, method_name = loads(content)
    except:
        raise Exception("invalid XMLRPC request: {0:s}".format(exc_string()))

    # the request contained a valid xmlrpc packet, it would be polite
    # to respond with one as well

    try:

        pmnc.log.debug("HTTP request {0:s} is promoted to XMLRPC call to {1:s}()".\
                       format(pmnc.request.unique_id, method_name))

        # populate the request parameters with XMLRPC-specific values

        pmnc.request.protocol = "xmlrpc"
        xmlrpc_request = dict(method = method_name, args = args)
        xmlrpc_response = dict(result = None)

        # invoke the application handler

        process_xmlrpc_request(xmlrpc_request, xmlrpc_response)

        # fetch the XMLRPC call result

        result = xmlrpc_response["result"]
        if result is None:
            result = ()

        # marshal the result in an XMLRPC packet

        content = dumps((result, ), methodresponse = True, encoding = response_encoding)

    except:
        error = exc_string()
        content = dumps(Fault(500, error), methodresponse = True, encoding = response_encoding) # 500 as in "Internal Server Error"
        pmnc.log.warning("XMLRPC call {0:s} to {1:s}() returns XMLRPC fault: {2:s}".\
                         format(pmnc.request.unique_id, method_name, error))
    else:
        pmnc.log.debug("XMLRPC call {0:s} to {1:s}() returns successfully".\
                       format(pmnc.request.unique_id, method_name))

    http_response["headers"]["content-type"] = "text/xml"
    http_response["content"] = content

###############################################################################

class Resource(TransactionalResource): # XMLRPC resource

    @typecheck
    def __init__(self, name, *,
                 server_address: (str, int),
                 connect_timeout: float,
                 ssl_key_cert_file: optional(os_path.isfile),
                 ssl_ca_cert_file: optional(os_path.isfile),
                 extra_headers: dict_of(str, str),
                 http_version: str,
                 server_uri: str,
                 request_encoding: str):

        TransactionalResource.__init__(self, name)

        self._server_address = server_address
        self._server_uri = server_uri
        self._request_encoding = request_encoding

        self._http_resource = \
            pmnc.protocol_http.Resource(name,
                                        server_address = server_address,
                                        connect_timeout = connect_timeout,
                                        ssl_key_cert_file = ssl_key_cert_file,
                                        ssl_ca_cert_file = ssl_ca_cert_file,
                                        extra_headers = extra_headers,
                                        http_version = http_version)

    ###################################

    def connect(self):
        self._attrs = []
        self._http_resource.connect()
        TransactionalResource.connect(self)

    def disconnect(self):
        self._http_resource.disconnect()
        TransactionalResource.disconnect(self)

    ###################################

    # overriding the following two methods allows the subordinate
    # HTTP resource to time out at the same time with this resource

    def set_idle_timeout(self, idle_timeout):
        self._http_resource.set_idle_timeout(idle_timeout)
        TransactionalResource.set_idle_timeout(self, idle_timeout)

    def set_max_age(self, max_age):
        self._http_resource.set_max_age(max_age)
        TransactionalResource.set_max_age(self, max_age)

    ###################################

    # therefore the _http_resource.expired won't cause
    # any unexpected timeouts, especially in the case
    # when the pool has its timeout increased

    def _expired(self):
        return self._http_resource.expired or \
               TransactionalResource._expired(self)

    ###################################

    def __getattr__(self, name):
        self._attrs.append(name)
        return self

    ###################################

    def __call__(self, *args):

        # marshal the request

        method, self._attrs = ".".join(self._attrs), []
        request = dumps(args, methodname = method, encoding = self._request_encoding)

        # send HTTP request containing the XMLRPC packet

        pmnc.log.info("sending XMLRPC request {0:s} to {1[0]:s}:{1[1]:d}".\
                      format(method, self._server_address))
        try:

            status_code, headers, content = \
                self._http_resource.post(self._server_uri, request.encode(self._request_encoding),
                                         { "Content-Type": "text/xml" })
            self._http_resource.reset_idle_timeout() # this is a hack, the timeout on the
                                                     # subordinate resource needs to be reset
            # see if the response is correct

            if status_code != 200:
                raise Exception("HTTP status code {0:d}".format(status_code))

            try:
                result = loads(content)
            except:
                raise Exception("invalid XMLRPC response: {0:s}".format(exc_string()))

            try:
                result = result[0][0]
            except:
                raise Exception("unexpected XMLRPC response format: {0:s}".\
                                format(exc_string()))

        except:
            pmnc.log.warning("XMLRPC request failed: {0:s}".format(exc_string()))
            raise
        else:
            pmnc.log.info("XMLRPC request returned successfully")

        return result

###############################################################################

def self_test():

    from socket import socket, AF_INET, SOCK_STREAM
    from pmnc.request import fake_request

    def sendall(ifc, data):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(ifc.listener_address)
        s.sendall(data)
        return s

    def recvall(s):
        result = b""
        data = s.recv(1024)
        while data:
            result += data
            data = s.recv(1024)
        return result

    rus = "\u0410\u0411\u0412\u0413\u0414\u0415\u0401\u0416\u0417\u0418\u0419" \
          "\u041a\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424" \
          "\u0425\u0426\u0427\u0428\u0429\u042c\u042b\u042a\u042d\u042e\u042f" \
          "\u0430\u0431\u0432\u0433\u0434\u0435\u0451\u0436\u0437\u0438\u0439" \
          "\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441\u0442\u0443\u0444" \
          "\u0445\u0446\u0447\u0448\u0449\u044c\u044b\u044a\u044d\u044e\u044f"

    def post_string(ifc, method, s, request_encoding):
        req = "<?xml version=\"1.0\" encoding=\"{0:s}\"?>" \
              "<methodCall><methodName>{1:s}</methodName>" \
              "<params><param><value><string>{2:s}</string>" \
              "</value></param></params></methodCall>".format(request_encoding, method, s).encode(request_encoding)
        hdr = "POST / HTTP/1.0\nContent-Type: text/xml\nContent-Length: {0:d}\n\n".format(len(req))
        s = sendall(ifc, hdr.encode(request_encoding) + req)
        resp = recvall(s)
        assert resp.startswith(b"HTTP/1.1 200 OK\r\n")
        resp = resp.split(b"\r\n\r\n", 1)[1]
        return loads(resp)[0][0]

    ################################### TESTING INTERFACE

    def start_interface(process_xmlrpc_request = None):

        def do_nothing(request, response):
            pass

        config = pmnc.config_interface_xmlrpc_1.copy()
        ifc = pmnc.interface.create("xmlrpc_1", **config)
        ifc.process_xmlrpc_request = process_xmlrpc_request or do_nothing
        ifc.start()
        return ifc

    ###################################

    def test_interface_start_stop():

        ifc = start_interface()
        ifc.cease(); ifc.stop()

    test_interface_start_stop()

    ###################################

    def test_interface_broken_requests():

        ifc = start_interface()
        try:

            s = sendall(ifc, b"POST / HTTP/1.0\nContent-Type: text/plain\n\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 415 Unsupported Media Type\r\n")

            s = sendall(ifc, b"POST / HTTP/1.0\nContent-Type: text/xml\nContent-Length: 3\n\nfoo")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\n")
            assert b"invalid XMLRPC request" in resp

        finally:
            ifc.cease(); ifc.stop()

    test_interface_broken_requests()

    ###################################

    def test_interface_marshaling():

        def test_interface_simple_pr(request, response):
            if request["method"] == "raise":
                raise Exception(request["args"][0])
            response["result"] = [request["method"], request["args"]]

        ifc = start_interface(test_interface_simple_pr)
        try:

            assert post_string(ifc, "MethodName", "foo", "utf-8") == ["MethodName", ["foo"]]
            assert post_string(ifc, rus, rus, "cp866") == [rus, [rus]]

            try:
                post_string(ifc, "raise", "foo", "iso-8859-5")
            except Fault as e:
                assert e.faultCode == 500 and e.faultString.startswith("Exception(\"foo\")")
            else:
                assert False

            try:
                post_string(ifc, "raise", rus, "utf-8")
            except Fault as e:
                assert e.faultCode == 500 and e.faultString.startswith("Exception(\"" + rus + "\")")
            else:
                assert False

        finally:
            ifc.cease(); ifc.stop()

    test_interface_marshaling()

    ################################### TESTING RESOURCE

    def test_resource_transaction():

        def res_transaction_pr(request, response):
            response["result"] = request, pmnc.request.parameters["auth_tokens"]

        ifc = start_interface(res_transaction_pr)
        try:

            fake_request(10.0)

            # usage in transaction, this utilizes config_resource_xmlrpc_1.py

            try:
                for i in range(19):
                    s = "*" * 2 ** i
                    xa = pmnc.transaction.create()
                    xa.xmlrpc_1.Module.Method(i, s, [ s ], { s: i })
                    assert xa.execute()[0] == [ { "method": "Module.Method", "args": [ i, s, [ s ], { s: i } ] },
                                                { "username": "user", "peer_ip": "127.0.0.1", "password": "pass", "encrypted": False } ]
            except Exception as e:
                assert ("time" in str(e)) or ("deadline" in str(e)), str(e)
            else:
                assert pmnc.request.elapsed < 10.0

        finally:
            ifc.cease(); ifc.stop()

    test_resource_transaction()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
