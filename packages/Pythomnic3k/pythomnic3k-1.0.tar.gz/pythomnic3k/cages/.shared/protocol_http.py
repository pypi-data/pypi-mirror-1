#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module contains an implementation of HTTP interface/resource.
#
# Sample HTTP interface configuration (config_interface_http_1.py):
#
# config = dict \
# (
# protocol = "http",                                               # meta
# listener_address = ("127.0.0.1", 8000),                          # tcp
# max_connections = 100,                                           # tcp
# ssl_key_cert_file = None,                                        # ssl
# ssl_ca_cert_file = None,                                         # ssl
# response_encoding = "ascii",                                     # http
# original_ip_header_fields = ("X-Forwarded-For", "X-Client-IP"),  # http
# allowed_methods = ("GET", "POST"),                               # http
# keep_alive_support = True,                                       # http
# keep_alive_idle_timeout = 60.0,                                  # http
# keep_alive_max_requests = 10,                                    # http
# )
#
# Sample processing module (interface_http_1.py):
#
# def process_request(request, response):
#     url = request["url"]
#     response["headers"]["content-type"] = "text/html"
#     response["content"] = "<html/>" # bytes or str if text/*
#
# Sample HTTP resource configuration (config_resource_http_1.py)
#
# config = dict \
# (
# protocol = "http",                                               # meta
# server_address = ("127.0.0.1", 8000),                            # tcp
# connect_timeout = 3.0,                                           # tcp
# ssl_key_cert_file = None,                                        # ssl
# ssl_ca_cert_file = None,                                         # ssl
# extra_headers = { "X-Foo": "Abc", "X-Bar": "Def" },              # http
# http_version = "HTTP/1.1",                                       # http
# )
#
# Sample resource usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.http_1.post("/", b"content", { "X-Biz": "Baz" })
# status_code, headers, content = xa.execute()[0]
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource", "Handler" ]

###############################################################################

import io; from io import BytesIO
import os; from os import SEEK_SET, SEEK_CUR, SEEK_END, path as os_path
import binascii; from binascii import a2b_base64
import itertools; from itertools import chain

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import typecheck; from typecheck import typecheck, optional, callable, \
                                        tuple_of, dict_of, by_regex
import exc_string; from exc_string import exc_string
import pmnc.timeout; from pmnc.timeout import Timeout
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource

###############################################################################

class Interface: # HTTP interface built on top of TCP pseudo-interface

    @typecheck
    def __init__(self, name: str, *,
                 listener_address: (str, int),
                 max_connections: int,
                 ssl_key_cert_file: optional(os_path.isfile),
                 ssl_ca_cert_file: optional(os_path.isfile),
                 response_encoding: str,
                 original_ip_header_fields: tuple_of(str),
                 allowed_methods: tuple_of(str),
                 keep_alive_support: bool,
                 keep_alive_idle_timeout: float,
                 keep_alive_max_requests: int,
                 **kwargs): # this kwargs allows for extra application-specific
                            # settings in config_interface_http_X.py

        # having handler factory create handlers through a pmnc call
        # allows online modifications to this module, after it is reloaded

        handler_factory = lambda prev_handler: \
            pmnc.protocol_http.Handler(prev_handler, self.process_http_request,
                                       response_encoding = response_encoding,
                                       original_ip_header_fields = original_ip_header_fields,
                                       allowed_methods = allowed_methods,
                                       keep_alive_support = keep_alive_support,
                                       keep_alive_idle_timeout = keep_alive_idle_timeout,
                                       keep_alive_max_requests = keep_alive_max_requests)

        # create an instance of underlying TCP interface

        self._tcp_interface = \
            pmnc.protocol_tcp.TcpInterface(name, handler_factory,
                                           listener_address = listener_address,
                                           max_connections = max_connections,
                                           ssl_key_cert_file = ssl_key_cert_file,
                                           ssl_ca_cert_file = ssl_ca_cert_file)

    name = property(lambda self: self._tcp_interface.name)
    listener_address = property(lambda self: self._tcp_interface.listener_address)

    ###################################

    def start(self):
        self._tcp_interface.start()

    def cease(self):
        self._tcp_interface.cease()

    def stop(self):
        self._tcp_interface.stop()

    ###################################

    @typecheck
    def process_http_request(self, http_request: dict, http_response: dict):

        # default behaviour is to invoke the application handler

        handler_module_name = "interface_{0:s}".format(self.name)
        pmnc.__getattr__(handler_module_name).process_request(http_request, http_response)

###############################################################################

_valid_header = by_regex("^[A-Za-z0-9_-]+$")
_valid_headers = dict_of(by_regex("^[A-Za-z0-9_-]+$"), str)

_valid_header_lc = by_regex("^[a-z0-9_-]+$")
_valid_headers_lc = dict_of(by_regex("^[a-z0-9_-]+$"), str)

_valid_http_version = by_regex("^HTTP/1\\.(0|1)$")

###############################################################################

class HttpMessageParser:

    _max_line_size = 8192 # in particular, this restricts the length of the URL
    _lws = " \t"
    _forbidden_headers = ("transfer-encoding", ) # forbidden in both requests and responses

    ###################################

    @typecheck
    def __init__(self, max_size: int):
        self._max_size = max_size
        self._stream, self._offset = BytesIO(), 0
        self._first_line, self._headers = True, {}
        self._header_line, self._content = None, None
        self._complete = False

    headers = property(lambda self: self._headers)
    content = property(lambda self: self._content.getvalue())

    ###################################

    @classmethod
    def _split_name_value(cls, namevalue, separator):
        try:
            name, value = namevalue.split(separator, 1)
        except ValueError:
            return namevalue.strip(cls._lws).lower(), ""
        else:
            return name.strip(cls._lws).lower(), value.strip(cls._lws)

    ###################################

    def _flush_header_line(self):

        if self._header_line is None:
            return

        name, value = self._split_name_value(self._header_line, ":")
        if not _valid_header_lc(name):
            raise Exception("invalid header field name")
        elif name in self._forbidden_headers:
            raise Exception("{0:s} is not supported".format(name))
        self._headers[name] = value

        self._header_line = None

    ###################################

    def _append_header_line(self, line):

        if line[0] in self._lws: # folded header line
            if self._header_line is None:
                raise Exception("unexpected folded header line")
            else:
                self._header_line += " " + line.strip(self._lws)
        else:
            self._flush_header_line()
            self._header_line = line.rstrip(self._lws)

    ###################################

    def _read_line(self) -> optional(str):

        self._stream.seek(self._offset, SEEK_SET)
        try:

            line = self._stream.readline()
            if line.endswith(b"\r\n"):
                if len(line) - 2 > self._max_line_size: # complete line of excessive length
                    raise Exception("line size exceeded")
                self._offset = self._stream.tell()
                return line[:-2].decode("ascii", "replace")
            elif line.endswith(b"\n"):
                if len(line) - 1 > self._max_line_size: # complete line of excessive length
                    raise Exception("line size exceeded")
                self._offset = self._stream.tell()
                return line[:-1].decode("ascii", "replace")
            elif len(line) > self._max_line_size: # incomplete line of excessive length
                raise Exception("line size exceeded")
            else: # incomplete line of acceptable length
                return None

        finally:
            self._stream.seek(0, SEEK_END)

    ###################################

    @typecheck
    def write(self, data: bytes) -> bool:

        if self._complete:
            raise Exception("no more data expected")

        self._stream.write(data)
        if self._stream.tell() > self._max_size:
            raise Exception("message size exceeded")

        while not self._content:
            line = self._read_line()
            if line is None:
                return False
            if self._first_line:
                self._parse_first_line(line)
                self._first_line = False
            elif line != "":
                self._append_header_line(line)
            else:
                self._flush_header_line()
                self._content, self._content_offset = BytesIO(), self._offset
                content_length = self._headers.get("content-length")
                if content_length is not None:
                    try:
                        content_length = int(content_length)
                    except ValueError:
                        raise Exception("invalid content length")
                    if content_length < 0:
                        raise Exception("negative content length")
                    elif content_length > self._max_size - self._offset:
                        raise Exception("content length plus header size exceeds message size")
                else:
                    content_length = self._default_content_length()
                self._content_length = content_length

        content_remain = self._content_offset + self._content_length - self._stream.tell()
        if content_remain == 0:
            if self._content_length > 0:
                self._stream.seek(self._content_offset, SEEK_SET)
                self._content.write(self._stream.read(self._content_length))
            self._complete = True
            return True
        elif content_remain > 0:
            return False
        else:
            raise Exception("content length exceeded")

###############################################################################

class HttpRequestParser(HttpMessageParser):

    def _parse_first_line(self, line):
        try:
            method, url, version = line.split(" ")
            self._method, self._url, self._version = \
                method.upper(), url, version.upper()
        except ValueError:
            raise Exception("invalid first line")

    def _default_content_length(self):
        self.headers["content-length"] = "0"
        return 0

    method = property(lambda self: self._method)
    url = property(lambda self: self._url)
    version = property(lambda self: self._version)

###############################################################################

class HttpResponseParser(HttpMessageParser):

    def _parse_first_line(self, line):
        try:
            version, status_code, status_description = line.split(" ", 2)
            self._version, self._status_code, self._status_description = \
                version.upper(), int(status_code), status_description
        except ValueError:
            raise Exception("invalid first line")

    def _default_content_length(self):
        if self.headers.get("connection", "close").lower() == "keep-alive":
            raise Exception("unspecified content length")
        return self._max_size - self._offset

    @typecheck
    def write(self, data: bytes) -> bool:
        if not data:
            if not self._content or "content-length" in self._headers:
                raise Exception("unexpected eof")
            else:
                self._content_length = self._stream.tell() - self._content_offset
                self.headers["content-length"] = str(self._content_length)
        return HttpMessageParser.write(self, data)

    version = property(lambda self: self._version)
    status_code = property(lambda self: self._status_code)
    status_description = property(lambda self: self._status_description)

###############################################################################

class HttpRequestValidateError(Exception):

    def __init__(self, status_code, message):
        Exception.__init__(self, "HTTP request parse error {0:d} ({1:s})".\
                                 format(status_code, message))
        self._status_code = status_code
        self._message = message

    status_code = property(lambda self: self._status_code)
    message = property(lambda self: self._message)

###############################################################################

class Handler: # this class is instantiated from interface_tcp

    protocol = "http"

    _max_request_size = 1048576

    _status_codes = \
    {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "(Unused)",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    }

    ###################################

    @typecheck
    def __init__(self, prev_handler,
                 process_http_request: callable,
                 response_encoding: str,
                 original_ip_header_fields: tuple_of(str),
                 allowed_methods: tuple_of(str),
                 keep_alive_support: bool,
                 keep_alive_idle_timeout: float,
                 keep_alive_max_requests: int):

        self._process_http_request = process_http_request
        self._response_encoding = response_encoding
        self._original_ip_header_fields = tuple(s.lower() for s in original_ip_header_fields)
        self._allowed_methods = allowed_methods

        # handle keep-alive related arguments, make an initial keep-alive decision

        self._use_count = (prev_handler is not None) and (prev_handler.use_count + 1) or 1
        self._keep_alive = keep_alive_support and self._use_count < keep_alive_max_requests
        self._idle_timeout = keep_alive_idle_timeout

        # this object will accumulate and parse the request data

        self._http_request = HttpRequestParser(self._max_request_size)

    use_count = property(lambda self: self._use_count)
    idle_timeout = property(lambda self: self._keep_alive and self._idle_timeout or 0.0)

    ###################################

    @typecheck
    def consume(self, data: bytes) -> bool:

        return self._http_request.write(data)

    ###################################

    @typecheck
    def _validate_http_request(self) -> (str, str, _valid_headers_lc, str, bytes):

        method = self._http_request.method
        if method not in self._allowed_methods:
            raise HttpRequestValidateError(405, "method not allowed")

        version = self._http_request.version
        if not _valid_http_version(version):
            raise HttpRequestValidateError(505, "unsupported http version")

        headers = self._http_request.headers

        if headers.get("content-encoding", "identity").lower() != "identity":
            raise HttpRequestValidateError(415, "unsupported content-encoding")

        if "range" in headers:
            raise HttpRequestValidateError(501, "range is not supported")

        if "transfer-encoding" in headers:
            raise HttpRequestValidateError(501, "transfer-encoding is not supported")

        url = self._http_request.url
        content = self._http_request.content

        return method, version, headers, url, content

    ###################################

    def _extract_auth_tokens(self, headers):

        auth_tokens = {}

        # extract username/password if present

        authorization = headers.get("authorization")
        if authorization is not None:
            if authorization.lower().startswith("basic "):
                credentials = HttpMessageParser._split_name_value(authorization, " ")[1]
                username, password = a2b_base64(credentials.encode("ascii")).decode("ascii").split(":", 1)
                auth_tokens["username"] = username
                auth_tokens["password"] = password
            else:
                raise HttpRequestValidateError(501, "authorization is not supported")

        # override the client's IP address from a configured request header field(s)

        for name in self._original_ip_header_fields:
            value = headers.get(name)
            if value:
                auth_tokens["peer_ip"] = value
                break

        return auth_tokens

    ###################################

    # this method is executed by one of the interface pool threads and performs
    # the actual processing of a previously read and parsed request

    def process_tcp_request(self):

        # this method should not throw, but wrap the exception in HTTP error response

        try:

            # perform preliminary request validation, this throws HttpRequestValidateError

            method, version, headers, url, content = self._validate_http_request()

            # extract username/password and override client IP

            auth_tokens = self._extract_auth_tokens(headers)
            pmnc.request.parameters["auth_tokens"].update(auth_tokens)

            # see whether the connection can actually be kept alive and insert a correct header

            if headers.get("connection", "close").lower() != "keep-alive":
                self._keep_alive = False
            headers["connection"] = self._keep_alive and "keep-alive" or "close"

            # populate request and response with HTTP-specific values

            request = dict(method = method, url = url, headers = headers, content = content)
            response = dict(status_code = 200, content = b"",
                            headers = { "content-type": "application/octet-stream",
                                        "connection": self._keep_alive and "keep-alive" or "close" })

            # execute the application-specific handler passed to the constructor

            self._process_http_request(request, response)

            # fetch and validate the returned response status code, possibly modified

            self._status_code = response["status_code"]
            assert self._status_code in self._status_codes, "invalid status code"

            # fetch and validate the returned response headers, possibly modified

            response_headers, response_headers_lc = response["headers"], {}
            for n, v in response_headers.items():
                if not _valid_header(n) or not isinstance(v, str):
                    raise Exception("invalid response headers, expected a dict of ascii str to str")
                else:
                    response_headers_lc[n.lower()] = v
            response_headers = response_headers_lc

            # handle response header Connection: field, this is the final keep-alive decision

            if response_headers.pop("connection", "close").lower() == "keep-alive" and self._status_code < 400:
                if not self._keep_alive:
                    raise Exception("unable to keep the connection alive")
            else:
                self._keep_alive = False

            # fetch and validate the returned response content, possibly modified

            response_content = response["content"]

            # encode textual output to bytes using the configured response encoding

            if isinstance(response_content, str):
                response_content_type = response_headers["content-type"].lower()
                assert response_content_type.startswith("text/"), "should have returned content-type text/* for str content"
                response_content = response_content.encode(self._response_encoding, "replace")
                response_headers["content-type"] = "{0:s}; charset={1:s}".format(response_content_type, self._response_encoding)

            assert isinstance(response_content, bytes), "should have returned bytes for response content"

            # compare and remove content-length field, will be overriden later

            response_content_length = response_headers.pop("content-length", None)
            if response_content_length is not None:
                try:
                    response_content_length = int(response_content_length)
                except ValueError:
                    raise Exception("invalid response content length")
                if response_content_length < 0:
                    raise Exception("negative response content length")
                assert response_content_length == len(response_content), "response content length mismatch"

            # drop content-type field if there is no content

            if not response_content:
                response_headers.pop("content-type", None)

            # turn the response headers dict into crlf-concatenated string

            response_header_fields = "\r\n".join("{0:s}: {1:s}".format(n.title(), v)
                                                 for n, v in response_headers.items())
            if response_header_fields: response_header_fields += "\r\n"

        except HttpRequestValidateError as e:
            pmnc.log.warning("HTTP request {0:s} returns parse error {1:d} ({2:s})".\
                             format(pmnc.request.unique_id, e.status_code, e.message))
            self._status_code = e.status_code
            response_content = b""
            response_header_fields = ""
            self._keep_alive = False
        except:
            error = exc_string()
            pmnc.log.warning("HTTP request {0:s} returns internal server error: {1:s}".\
                             format(pmnc.request.unique_id, error))
            self._status_code = 500
            response_content = error.encode(self._response_encoding, "replace")
            response_header_fields = "Content-Type: text/plain; charset={0:s}\r\n".\
                                     format(self._response_encoding)
            self._keep_alive = False
        else:
            pmnc.log.debug("HTTP request {0:s} returns response {1:d} {2:s} with {3:d} "
                           "content byte(s)".format(pmnc.request.unique_id, self._status_code,
                                                    self._status_codes[self._status_code],
                                                    len(response_content)))

        # wrap and return whatever response we got, possibly an internal error

        status_code_description = self._status_codes[self._status_code]

        if response_content or self._keep_alive:
            response_header = "HTTP/1.1 {0:d} {1:s}\r\n" \
                              "Connection: {2:s}\r\n" \
                              "Cache-Control: no-cache\r\n" \
                              "Pragma: no-cache\r\n" \
                              "Content-Length: {3:d}\r\n" \
                              "{4:s}\r\n".\
                              format(self._status_code, status_code_description,
                                     self._keep_alive and "keep-alive" or "close",
                                     len(response_content),
                                     response_header_fields)
        else:
            response_header = "HTTP/1.1 {0:d} {1:s}\r\n" \
                              "Connection: close\r\n" \
                              "Cache-Control: no-cache\r\n" \
                              "Pragma: no-cache\r\n" \
                              "{2:s}\r\n".\
                              format(self._status_code, status_code_description,
                                     response_header_fields)

        self._response_stream = BytesIO(response_header.encode("ascii", "replace") + response_content)

    ###################################

    @typecheck
    def produce(self, n: int) -> bytes:

        return self._response_stream.read(n)

    ###################################

    @typecheck
    def retract(self, n: int):

        self._response_stream.seek(-n, SEEK_CUR)

###############################################################################

class Resource(TransactionalResource): # HTTP resource

    _max_response_size = 16777216

    @typecheck
    def __init__(self, name, *,
                 server_address: (str, int),
                 connect_timeout: float,
                 ssl_key_cert_file: optional(os_path.isfile),
                 ssl_ca_cert_file: optional(os_path.isfile),
                 extra_headers: _valid_headers,
                 http_version: _valid_http_version):

        TransactionalResource.__init__(self, name)

        self._host = server_address[1] != 80 and \
                     "{0[0]:s}:{0[1]:d}".format(server_address) or server_address[0]
        self._server_address = server_address
        self._extra_headers = extra_headers
        self._http_version = http_version

        self._tcp_resource = \
            pmnc.protocol_tcp.TcpResource(name,
                                          server_address = server_address,
                                          connect_timeout = connect_timeout,
                                          ssl_key_cert_file = ssl_key_cert_file,
                                          ssl_ca_cert_file = ssl_ca_cert_file)

    ###################################

    def connect(self):
        self._tcp_resource.connect()
        TransactionalResource.connect(self)

    def disconnect(self):
        self._tcp_resource.disconnect()
        TransactionalResource.disconnect(self)

    ###################################

    @typecheck
    def response_handler(self, data: bytes):

        if self._response.write(data):
            return self._response.status_code, self._response.headers, self._response.content
        else:
            return None

    ###################################

    @typecheck
    def _fmt(self, method, url, headers: _valid_headers, body) -> bytes:

        content_length = headers.pop("content-length", None)
        if content_length is not None:
            try:
                content_length = int(content_length)
            except ValueError:
                raise Exception("invalid content length")
            if content_length < 0:
                raise Exception("negative content length")
            if content_length != len(body):
                raise Exception("request content length mismatch")
        else:
            content_length = len(body)
        headers["content-length"] = str(content_length)

        headers.setdefault("connection", "keep-alive")
        headers.setdefault("cache-control", "no-cache")
        headers.setdefault("pragma", "no-cache")
        headers.setdefault("host", self._host)

        header_fields = "\r\n".join("{0:s}: {1:s}".format(n.title(), v)
                                    for n, v in headers.items())

        return "{0:s} {1:s} {2:s}\r\n" \
               "{3:s}\r\n" \
               "\r\n".\
               format(method, url, self._http_version, header_fields).encode("ascii", "replace") \
               + body

    ###################################

    def req(self, method, url, body, headers):

        headers = { n.lower(): v.strip(HttpMessageParser._lws)
                    for n, v in chain(self._extra_headers.items(), headers.items()) }
        request = self._fmt(method, url, headers, body)
        self._response = HttpResponseParser(self._max_response_size)

        pmnc.log.debug("sending HTTP request {0:s} {1:s} + {2:d} content byte(s) to "
                       "{3[0]:s}:{3[1]:d}".format(method, url, len(body), self._server_address))
        try:
            status_code, headers, content = \
                self._tcp_resource.send_request(request, self.response_handler)
        except:
            pmnc.log.warning("HTTP request failed: {0:s}".format(exc_string()))
            raise
        else:
            pmnc.log.debug("HTTP request returned status code {0:d}".\
                           format(status_code))

        if headers.get("connection", "close").lower() != "keep-alive":
            self.expire()

        return status_code, headers, content

    ###################################

    @typecheck
    def get(self, url: str, headers: optional(_valid_headers) = {}) -> (int, _valid_headers_lc, bytes):

        return self.req("GET", url, b"", headers)

    @typecheck
    def post(self, url: str, body: bytes, headers: optional(_valid_headers) = {}) -> (int, _valid_headers_lc, bytes):

        return self.req("POST", url, body, headers)

###############################################################################

def self_test():

    from socket import socket, AF_INET, SOCK_STREAM, error as socket_error
    from pickle import dumps as pickle, loads as unpickle
    from time import sleep
    from threading import current_thread, Thread
    from expected import expected
    from typecheck import InputParameterError
    from select import select
    from pmnc.request import fake_request

    rus_abc = "\u0430\u0431\u0432".encode("windows-1251")

    ################################### TESTING HTTP PARSER

    def test_parser_large_request():

        hr = HttpRequestParser(1)
        with expected(Exception("message size exceeded")):
            hr.write(b"foo")

    test_parser_large_request()

    ###################################

    def test_parser_long_line():

        hr = HttpRequestParser(10)
        hr._max_line_size = 2
        hr.write(b"12")
        with expected(Exception("line size exceeded")):
            hr.write(b"3")

        hr = HttpRequestParser(10)
        hr._max_line_size = 2
        with expected(Exception("line size exceeded")):
            hr.write(b"123\r\n")

        hr = HttpRequestParser(10)
        hr._max_line_size = 2
        with expected(Exception("invalid first line")):
            hr.write(b"12\r\n")

    test_parser_long_line()

    ###################################

    def test_parser_request_first_line():

        hr = HttpRequestParser(1024)
        with expected(Exception("invalid first line")):
            hr.write(b"FOO\r\n")

        hr = HttpRequestParser(1024)
        with expected(Exception("invalid first line")):
            hr.write(b"FOO BAR\r\n")

        hr = HttpRequestParser(1024)
        assert not hr.write(b"FOO BAR BIZ\r\n")
        assert hr.method == "FOO" and hr.url == "BAR" and hr.version == "BIZ"

    test_parser_request_first_line()

    ###################################

    def test_parser_response_first_line():

        hr = HttpResponseParser(1024)
        with expected(Exception("invalid first line")):
            hr.write(b"FOO\r\n")

        hr = HttpResponseParser(1024)
        with expected(Exception("invalid first line")):
            hr.write(b"FOO BAR\r\n")

        hr = HttpResponseParser(1024)
        with expected(Exception("invalid first line")):
            hr.write(b"FOO BAR BIZ\r\n")

        hr = HttpResponseParser(1024)
        assert not hr.write(b"FOO 200 BIZ BAZ\r\n")
        assert hr.version == "FOO" and hr.status_code == 200 and hr.status_description == "BIZ BAZ"

    test_parser_response_first_line()

    ###################################

    def test_parser_headers():

        hr = HttpRequestParser(1024)
        assert not hr.write(b"GET / HTTP/1.0\r\nA#1: foo\r\n")
        assert not hr.write(b"\tbar\r\n")
        with expected(Exception("invalid header field name")):
            hr.write(b"\r\n")

        hr = HttpRequestParser(1024)
        assert not hr.write(b"GET / HTTP/1.0\r\n")
        with expected(Exception("unexpected folded header line")):
            assert not hr.write(b"\tfoo\r\n")

        hr = HttpRequestParser(1024)
        assert hr.write(b"GET / HTTP/1.0\r\nRus: " + rus_abc + b"\n\n")
        assert hr.headers == { "content-length": "0", "rus": "\ufffd\ufffd\ufffd" }

        hr = HttpRequestParser(1024)
        assert not hr.write(b"GET / HTTP/1.0\n")
        assert not hr.write(b"Foo: 123   \n")
        assert not hr.write(b"     456      \n")
        assert not hr.write(b"X-BIZ   :    \t BAZ \t  \n")
        assert not hr.write(b"DUP: 1\nDUP: 2\n")
        assert not hr.write(b"\r")
        assert hr.write(b"\n")
        assert hr.headers == { "content-length": "0", "foo": "123 456", "x-biz": "BAZ", "dup": "2" }

    test_parser_headers()

    ###################################

    def test_parser_content():

        hr = HttpRequestParser(1024)
        assert hr.write(b"GET / HTTP/1.0\r\n\r\n")
        assert hr.content == b"" and hr.headers["content-length"] == "0"

        hr = HttpRequestParser(1024)
        with expected(Exception("invalid content length")):
            hr.write(b"GET / HTTP/1.0\r\nContent-Length: foo\r\n\r\n")

        hr = HttpRequestParser(1024)
        with expected(Exception("invalid content length")):
            hr.write(b"GET / HTTP/1.0\r\nContent-Length: foo\r\n\r\n")

        hr = HttpRequestParser(1024)
        with expected(Exception("negative content length")):
            hr.write(b"GET / HTTP/1.0\r\nContent-Length: -1\r\n\r\n")

        hr = HttpRequestParser(999)
        r = "GET / HTTP/1.0\r\nContent-Length: {0}\r\n\r\n"
        with expected(Exception("content length plus header size exceeds message size")):
            hr.write(r.format(999 - len(r) + 1).encode("ascii"))

        hr = HttpRequestParser(1024)
        assert not hr.write(b"GET / HTTP/1.0\r\nCONTENT-LENGTH:3\r\n\r\n")
        assert not hr.write(b"1")
        assert not hr.write(b"2")
        assert hr.write(b"3")
        assert hr.headers == { "content-length": "3" } and hr.content == b"123"

        hr = HttpRequestParser(1024)
        assert not hr.write(b"GET / HTTP/1.0\r\nCONTENT-LENGTH:3\r\n\r\n")
        assert hr.write(rus_abc)
        assert hr.headers == { "content-length": "3" } and hr.content == rus_abc

        hr = HttpRequestParser(1024)
        assert not hr.write(b"GET / HTTP/1.0\r\nCONTENT-LENGTH:3\r\n\r\n")
        with expected(Exception("content length exceeded")):
            hr.write(b"1234")

        # response behaves differently with respect to unspecified content length and eof

        hr = HttpRequestParser(1024)
        assert hr.write(b"GET / HTTP/1.0\r\n\r\n")
        assert hr.headers["content-length"] == "0"
        with expected(Exception("no more data expected")):
            hr.write(b"foo")

        hr = HttpResponseParser(1024)
        assert not hr.write(b"HTTP/1.0 200 OK\r\n\r\n")
        assert "content-length" not in hr.headers
        assert not hr.write(b"foo")
        assert "content-length" not in hr.headers
        assert hr.write(b"")
        assert hr.headers["content-length"] == "3"
        with expected(Exception("no more data expected")):
            hr.write(b"foo")

        hr = HttpResponseParser(20)
        assert not hr.write(b"HTTP/1.0 200 OK\r\n\r\n")
        assert "content-length" not in hr.headers
        with expected(Exception("message size exceeded")):
            hr.write(b"12")

        hr = HttpResponseParser(1024)
        with expected(Exception("unspecified content length")):
            hr.write(b"HTTP/1.0 200 OK\r\nConnection: keep-alive\r\n\r\n")

    test_parser_content()

    ################################### TESTING INTERFACE

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

    def peer_drops_connection(s):
        return recvall(s) == b""

    def recvresp(s):
        result = b""
        max_len = 100000
        while len(result) < max_len:
            result += s.recv(1024)
            if b"\r\n\r\n" in result:
                hdr = result.split(b"\r\n\r\n", 1)[0]
                max_len = [int(s.split(b" ", 1)[1])
                           for s in hdr.split(b"\r\n")
                           if s.startswith(b"Content-Length: ")][0] + len(hdr) + 4
        return result

    ###################################

    def start_interface(process_http_request, **kwargs):

        config = pmnc.config_interface_http_1.copy()
        config.update(kwargs)
        ifc = pmnc.interface.create("http_1", **config)
        ifc.process_http_request = process_http_request
        ifc.start()
        return ifc

    ###################################

    # testing interface start/stop

    def test_interface_start_stop():

        def start_stop_pr(request, response):
            assert False, "should not see me"

        ifc = start_interface(start_stop_pr)
        ifc.cease(); ifc.stop()

    test_interface_start_stop()

    ###################################

    def test_interface_broken_requests():

        def broken_requests_pr(request, response):
            response["content"] = pickle(request["headers"])

        ifc = start_interface(broken_requests_pr)
        try:

            # single line too long

            s = sendall(ifc, b"*" * (HttpMessageParser._max_line_size + 1))
            assert peer_drops_connection(s)

            # wacked

            s = sendall(ifc, b"\n") # accepts just LFs
            assert peer_drops_connection(s)

            # HTTP 0.9 (?)

            s = sendall(ifc, b"GET /\r\n\r\n")
            assert peer_drops_connection(s)

            # request too large

            s = sendall(ifc, b"GET / HTTP/1.0\r\n" +
                             (b"X-Foo: " + b"*" * (HttpMessageParser._max_line_size - 7) + b"\r\n") *
                              (Handler._max_request_size // HttpMessageParser._max_line_size))
            assert peer_drops_connection(s)

            # HTTP 2.0

            s = sendall(ifc, b"GET / HTTP/2.0\n\r\n") # mixed CRLFs are fine
            assert recvall(s) == b"HTTP/1.1 505 HTTP Version Not Supported\r\nConnection: close\r\n" \
                                 b"Cache-Control: no-cache\r\nPragma: no-cache\r\n\r\n"

            # invalid method

            s = sendall(ifc, b"DELETE / HTTP/1.0\r\n\r\n")
            assert recvall(s) == b"HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n" \
                                 b"Cache-Control: no-cache\r\nPragma: no-cache\r\n\r\n"

            # broken header

            s = sendall(ifc, b"GET / HTTP/1.0\r\n$$$\r\n\r\n")
            assert peer_drops_connection(s)

            # broken header #2

            s = sendall(ifc, b"GET / HTTP/1.0\r\n#$@: foo\r\n\r\n")
            resp = recvall(s)
            assert peer_drops_connection(s)

            # semi-broken header (non-ascii value)

            s = sendall(ifc, b"GET / HTTP/1.0\r\nX-Foo: " + rus_abc + b"\r\n\r\n")
            resp = recvall(s)
            headers = unpickle(resp.split(b"\r\n\r\n", 1)[1])
            assert headers == { "content-length": "0", "connection": "close", "x-foo": "\ufffd\ufffd\ufffd" }

            # content-encoding: only identity is supported

            s = sendall(ifc, b"GET / HTTP/1.0\r\nContent-Encoding: identity\r\n\r\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 200 OK\r\n")

            s = sendall(ifc, b"GET / HTTP/1.0\r\nContent-Encoding: gzip\r\n\r\n")
            resp = recvall(s)
            assert resp == b"HTTP/1.1 415 Unsupported Media Type\r\nConnection: close\r\n" \
                           b"Cache-Control: no-cache\r\nPragma: no-cache\r\n\r\n"

            # transfer-encoding: not supported, but results in a different kind of failure

            s = sendall(ifc, b"GET / HTTP/1.0\r\nTransfer-Encoding: chunked\r\n\r\n")
            resp = recvall(s)
            assert peer_drops_connection(s)

            # range: not supported

            s = sendall(ifc, b"GET / HTTP/1.0\r\nRange: bytes=0-100\r\n\r\n")
            resp = recvall(s)
            assert resp == b"HTTP/1.1 501 Not Implemented\r\nConnection: close\r\n" \
                           b"Cache-Control: no-cache\r\nPragma: no-cache\r\n\r\n"

        finally:
            ifc.cease(); ifc.stop()

    test_interface_broken_requests()

    ###################################

    def test_interface_errors():

        def errors_pr(request, response):
            raise Exception(request["content"].decode(request["headers"]["x-content-charset"]))

        ifc = start_interface(errors_pr)
        try:

            # produce internal server error

            s = sendall(ifc, b"GET / HTTP/1.0\r\nContent-Length: 3\r\nX-Content-Charset: ascii\r\n\r\nfoo")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\n")
            assert b"Exception(\"foo\")" in resp

            # now with international chars

            s = sendall(ifc, b"GET / HTTP/1.0\r\nContent-Length: 6\r\nX-Content-Charset: windows-1251\r\n\r\nfoo" + rus_abc)
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\n")
            assert b"Exception(\"foo???\")" in resp

        finally:
            ifc.cease(); ifc.stop()

    test_interface_errors()

    ###################################

    def test_interface_authorization():

        def authorization_pr(request, response):
            response["content"] = pickle(pmnc.request.parameters["auth_tokens"])

        ifc = start_interface(authorization_pr)
        try:

            # ip authorization

            s = sendall(ifc, b"GET / HTTP/1.0\r\n\r\n")
            resp = recvall(s)
            auth_tokens = unpickle(resp.split(b"\r\n\r\n", 1)[1])
            assert auth_tokens == { "peer_ip": "127.0.0.1", "encrypted": False }

            # ip authorization with override

            s = sendall(ifc, b"GET / HTTP/1.0\r\nX-CLIENT-IP: 1.2.3.4\r\n\r\n") # foo:bar
            resp = recvall(s)
            auth_tokens = unpickle(resp.split(b"\r\n\r\n", 1)[1])
            assert auth_tokens == { "peer_ip": "1.2.3.4", "encrypted": False }

            # basic authorization with two ip overrides

            s = sendall(ifc, b"GET / HTTP/1.0\r\nX-CLIENT-IP: 1.2.3.4\r\nx-fOrWaRdEd-fOr: 5.6.7.8\r\n" \
                             b"Authorization: Basic Zm9vOmJhcg==\r\n\r\n") # foo:bar
            resp = recvall(s)
            auth_tokens = unpickle(resp.split(b"\r\n\r\n", 1)[1])
            assert auth_tokens == { "peer_ip": "5.6.7.8", "username": "foo", "password": "bar", "encrypted": False }

            # invalid authorization

            s = sendall(ifc, b"GET / HTTP/1.0\r\nAuthorization: void (it's+me+believe+me)\r\n\r\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 501 Not Implemented\r\n")

        finally:
            ifc.cease(); ifc.stop()

    test_interface_authorization()

    ###################################

    def test_interface_marshaling():

        def marshaling_pr(request, response):
            response["content"] = pickle(request)

        ifc = start_interface(marshaling_pr)
        try:

            s = sendall(ifc, b"POST /foo+bar%00x HTTP/1.0\r\nX-Field-1: VALUE-1\r\nX-Field-2: value-2\r\n"
                             b"Folded: foo\n bar \n\tbiz\t\r\n \tbaz\t \r\nContent-length: 3\r\n\r\nfoo")
            resp = recvall(s)
            resp_request = unpickle(resp.split(b"\r\n\r\n", 1)[1])
            assert resp_request == { "content": b"foo", "url": "/foo+bar%00x", "method": "POST",
                                     "headers": { "connection": "close", "x-field-1": "VALUE-1", "x-field-2": "value-2",
                                                  "content-length": "3", "folded": "foo bar biz baz" } }

        finally:
            ifc.cease(); ifc.stop()

    test_interface_marshaling()

    ###################################

    def test_interface_text_bytes():

        def text_bytes_pr(request, response):
            if "x-response-type" in request["headers"]:
                response["headers"]["content-type"] = request["headers"]["x-response-type"]
            if "x-request-encoding" in request["headers"]:
                response["content"] = request["content"].decode(request["headers"]["x-request-encoding"])
            else:
                response["content"] = request["content"]

        ifc = start_interface(text_bytes_pr)
        try:

            # by default returns bytes + application/octet-stream

            s = sendall(ifc, b"POST / HTTP/1.1\r\nContent-Length: 3\r\nContent-Type: text/plain\r\n\r\nfoo")
            resp = recvall(s)
            assert resp ==  b"HTTP/1.1 200 OK\r\nConnection: close\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                            b"Content-Length: 3\r\nContent-Type: application/octet-stream\r\n\r\nfoo"

            # encodes str using interface encoding

            s = sendall(ifc, b"POST / HTTP/1.1\r\nContent-Length: 3\r\nContent-Type: text/plain\r\n"
                             b"X-Response-Type: text/plain\r\nX-Request-Encoding: ascii\r\n\r\nfoo")
            resp = recvall(s)
            assert resp ==  b"HTTP/1.1 200 OK\r\nConnection: close\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                            b"Content-Length: 3\r\nContent-Type: text/plain; charset=ascii\r\n\r\nfoo"

            # replacing unknown chars with "?"

            s = sendall(ifc, b"POST / HTTP/1.1\r\nContent-Length: 6\r\nContent-Type: text/plain\r\n"
                             b"X-Response-Type: text/plain\r\nX-Request-Encoding: windows-1251\r\n\r\nfoo" + rus_abc)
            resp = recvall(s)
            assert resp ==  b"HTTP/1.1 200 OK\r\nConnection: close\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                            b"Content-Length: 6\r\nContent-Type: text/plain; charset=ascii\r\n\r\nfoo???"

            # can't return str + not text/*

            s = sendall(ifc, b"POST / HTTP/1.1\r\nContent-Length: 3\r\nContent-Type: text/plain\r\n"
                             b"X-Response-Type: image/gif\r\nX-Request-Encoding: ascii\r\n\r\nfoo")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\n")
            assert b"should have returned content-type text/* for str content" in resp

            # but can return bytes + text/* (who cares)

            s = sendall(ifc, b"POST / HTTP/1.1\r\nContent-Length: 3\r\nContent-Type: text/plain\r\n" \
                             b"X-Response-Type: text/xml\r\n\r\nfoo")
            resp = recvall(s)
            assert resp == b"HTTP/1.1 200 OK\r\nConnection: close\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                           b"Content-Length: 3\r\nContent-Type: text/xml\r\n\r\nfoo"

        finally:
            ifc.cease(); ifc.stop()

    test_interface_text_bytes()

    ###################################

    def test_interface_handling():

        def handling_pr(request, response):
            status_code, headers, content = unpickle(request["content"])
            response["status_code"] = status_code
            response["headers"].clear()
            response["headers"].update(headers)
            response["content"] = content

        ifc = start_interface(handling_pr)
        try:

            def post_error(status_code, headers, content):
                request = pickle((status_code, headers, content))
                s = sendall(ifc, "POST / HTTP/1.0\r\nconTENT-LENgth: {0:d}\r\n\r\n".format(len(request)).encode("ascii") + request)
                resp = recvall(s)
                assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\nConnection: close\r\n")
                return resp.split(b"\r\n\r\n")[1].decode("ascii")

            assert "invalid status code" in post_error("200", {}, b"")
            assert "invalid status code" in post_error(777, {}, b"")
            assert "unable to keep the connection alive" in post_error(200, { "Connection": "KEEP-ALIVE" }, b"")
            assert "invalid response headers, expected a dict of ascii str to str" in post_error(200, { "X#1": "foo" }, b"")
            assert "invalid response headers, expected a dict of ascii str to str" in post_error(200, { 1: "foo" }, b"")
            assert "invalid response headers, expected a dict of ascii str to str" in post_error(200, { "foo": 1 }, b"")
            assert "invalid response headers, expected a dict of ascii str to str" in post_error(200, { rus_abc: "foo" }, b"")

            assert "invalid response content length" in post_error(200, { "Content-Length": "foo" }, b"")
            assert "negative response content length" in post_error(200, { "Content-Length": "-1" }, b"")
            assert "response content length mismatch" in post_error(200, { "Content-Length": "2" }, b"foo")

        finally:
            ifc.cease(); ifc.stop()

    test_interface_handling()

    ###################################

    def test_interface_keep_alive():

        def keep_alive_pr(request, response):
            assert pmnc.request.interface == "http_1"
            assert pmnc.request.protocol == "http"
            if "x-error" in request["headers"]:
                raise Exception(request["headers"]["x-error"])
            response["content"] = request["headers"]["connection"].encode("ascii")
            if "x-response-connection" in request["headers"]:
                response["headers"]["connection"] = request["headers"]["x-response-connection"]

        ifc = start_interface(keep_alive_pr)
        try:

            # invalid requests cancel keep-alives

            s = sendall(ifc, b"OPTIONS / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n")
            resp = recvall(s)
            assert resp == b"HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n" \
                           b"Cache-Control: no-cache\r\nPragma: no-cache\r\n\r\n"

            # so do application-level exceptions

            s = sendall(ifc, b"GET / HTTP/1.1\r\nConnection: keep-alive\r\nX-Error: " + rus_abc + b"\r\n\r\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\nConnection: close\r\n")
            assert b"Exception(\"???\")" in resp

            # invalid value counts as close

            s = sendall(ifc, b"GET / HTTP/1.1\r\nConnection: foo\r\n\r\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 200 OK\r\nConnection: close\r\n")
            resp = resp.split(b"\r\n\r\n", 1)[1]
            assert resp == b"close"

            # application can override keep-alive -> close

            s = sendall(ifc, b"GET / HTTP/1.1\r\nConnection: keep-alive\r\nX-Response-Connection: close\r\n\r\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 200 OK\r\nConnection: close\r\n")
            resp = resp.split(b"\r\n\r\n", 1)[1]
            assert resp == b"keep-alive"

            # but not vice versa

            s = sendall(ifc, b"GET / HTTP/1.1\r\nConnection: close\r\nX-Response-Connection: keep-alive\r\n\r\n")
            resp = recvall(s)
            assert resp.startswith(b"HTTP/1.1 500 Internal Server Error\r\nConnection: close\r\n")
            assert b"unable to keep the connection alive" in resp

            # number of keep-alive requests over a single connections is limited

            s = sendall(ifc, b"GET / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n")
            assert recvresp(s) == b"HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                                  b"Content-Length: 10\r\nContent-Type: application/octet-stream\r\n\r\nkeep-alive"

            s.sendall(b"GET / HTTP/1.0\r\nConnection: keep-alive\r\n\r\n") # HTTP/1.0 client can have it too if asked
            assert recvresp(s) == b"HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                                  b"Content-Length: 10\r\nContent-Type: application/octet-stream\r\n\r\nkeep-alive"

            s.sendall(b"GET / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n")
            assert recvall(s) == b"HTTP/1.1 200 OK\r\nConnection: close\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                                 b"Content-Length: 5\r\nContent-Type: application/octet-stream\r\n\r\nclose"

            # keep-alive connection times out

            s = sendall(ifc, b"GET / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n")
            assert recvresp(s) == b"HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\nPragma: no-cache\r\n" \
                                  b"Content-Length: 10\r\nContent-Type: application/octet-stream\r\n\r\nkeep-alive"

            sleep(4.0)

            try:
                s.sendall(b"GET / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n")
                peer_drops_connection(s)
            except socket_error:
                pass

        finally:
            ifc.cease(); ifc.stop()

    test_interface_keep_alive()

    ################################### TESTING RESOURCE

    resource_config = dict \
    (
    server_address = None, # specified in each individual test
    connect_timeout = 1.0,
    ssl_key_cert_file = None,
    ssl_ca_cert_file = None,
    extra_headers = { "X-Foo": "Default", "X-Bar": "ABC" },
    http_version = "HTTP/1.1",
    )

    class TcpResponder:

        _anchor_s = None

        @typecheck
        def __init__(self, response: bytes, close: bool):
            self._response = response
            self._close = close

        def start(self):
            self._s = socket(AF_INET, SOCK_STREAM)
            self._s.bind(("127.0.0.1", 0))
            self._listener_address = self._s.getsockname()
            self._s.listen(256)
            self._th = Thread(target = self._respond)
            self._th.start()

        listener_address = property(lambda self: self._listener_address)

        def _respond(self):
            assert select([self._s], [], [], 3.0)[0], "no connection"
            s = self._s.accept()[0]
            s.recv(1024)
            s.sendall(self._response)
            if self._close:
                s.close()
            else:
                self.__class__._anchor_s = s

        def stop(self):
            self._th.join()
            self._s.close()
            if self.__class__._anchor_s:
                self.__class__._anchor_s.close()
                self.__class__._anchor_s = None

    def responder_request(url, headers, response, close):

        tr = TcpResponder(response, close)
        tr.start()
        try:

            resource_config["server_address"] = tr.listener_address
            fake_request(3.0)

            rc = pmnc.protocol_http.Resource("loopback", **resource_config)
            rc.connect()
            try:
                return rc.get(url, headers)
            finally:
                rc.disconnect()

        finally:
            tr.stop()

    ###################################

    def test_resource_garbage():

        with expected(Exception("unexpected eof")):
            responder_request("/", {}, b"foo", True)

        with expected(Exception("request deadline reading data from loopback tcp://127.0.0.1:")):
            responder_request("/", {}, b"foo", False)

        with expected(Exception("invalid first line")):
            responder_request("/", {}, b"foo\r\n", True)

        with expected(Exception("invalid first line")):
            responder_request("/", {}, b"foo\r\n", False)

        with expected(Exception("invalid first line")):
            responder_request("/", {}, b"foo bar biz\r\n\r\n", True)

        with expected(Exception("invalid first line")):
            responder_request("/", {}, b"foo bar biz\r\n\r\n", False)

        assert responder_request("/", {}, b"foo 200 biz\r\n\r\n", True) == (200, { "content-length": "0" }, b"")

        with expected(Exception("request deadline reading data from loopback tcp://127.0.0.1:")):
            responder_request("/", {}, b"foo 200 biz\r\n\r\n", False)

    test_resource_garbage()

    ###################################

    def test_resource_server_misbehaves():

        with expected(Exception("unexpected eof")):
            responder_request("/", {}, b"HTTP/1.0 200 OK", True)

        with expected(Exception("request deadline reading data from loopback tcp://127.0.0.1:")):
            responder_request("/", {}, b"HTTP/1.0 200 OK", False)

        with expected(Exception("unexpected eof")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\n", True)

        with expected(Exception("request deadline reading data from loopback tcp://127.0.0.1:")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\n", False)

        with expected(Exception("invalid header field name")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\n$$$: ###\nfoo: bar\n", True)

        with expected(Exception("invalid header field name")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\n$$$: ###\nfoo: bar\n", False)

        with expected(Exception("invalid content length")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\nContent-length:" + rus_abc + b"\n\n", True)

        with expected(Exception("invalid content length")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\nContent-length:" + rus_abc + b"\n\n", False)

        with expected(Exception("negative content length")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\nContent-length:-2342342348762384762\n\n", True)

        with expected(Exception("negative content length")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\nContent-length:-2342342348762384762\n\n", False)

        with expected(Exception("content length exceeded")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\nContent-length:4\n\n12345", True)

        with expected(Exception("content length exceeded")):
            responder_request("/", {}, b"HTTP/1.0 200 OK\nContent-length:4\n\n12345", False)

    test_resource_server_misbehaves()

    ###################################

    def test_resource_client_misbehaves():

        resource_config["server_address"] = ("1.2.3.4", 1234)

        rc = pmnc.protocol_http.Resource("test_resource_client_misbehaves", **resource_config)
        with expected(InputParameterError("get() has got an incompatible value for url")):
            rc.get(None)

        with expected(InputParameterError("get() has got an incompatible value for headers")):
            rc.get("/", { "#": "foo" })

        with expected(InputParameterError("get() has got an incompatible value for headers")):
            rc.get("/", { "foo": 1 })

        with expected(Exception("invalid content length")):
            rc.get("/", { "X-Foo": "bar", "Content-Length": "foo" })

        with expected(Exception("negative content length")):
            rc.get("/", { "X-Foo": "bar", "Content-length": "-1" })

        with expected(Exception("request content length mismatch")):
            rc.get("/", { "X-Foo": "bar", "Content-length": "1" })

        with expected(Exception("request content length mismatch")):
            rc.post("/", b"foo", { "X-Foo": "bar", "Content-length": "2" })

    test_resource_client_misbehaves()

    ###################################

    def test_resource_loopback():

        def res_loopback_pr(request, response):
            response["content"] = pickle(request)
            response["headers"]["content-type"] = "foo/bar"
            extra_response_headers = request["headers"].get("x-response-headers")
            if extra_response_headers:
                extra_response_headers = { s.split("=", 1)[0]: s.split("=", 1)[1]
                                           for s in extra_response_headers.split(";") }
                response["headers"].update(extra_response_headers)

        ifc = start_interface(res_loopback_pr)
        try:

            resource_config["server_address"] = ifc.listener_address
            fake_request(3.0)

            rc = pmnc.protocol_http.Resource("test_resource_loopback", **resource_config)
            rc.connect()
            try:

                # empty GET

                status_code, headers, content = rc.get("/", { "x-foo": "Override" })
                assert status_code == 200
                assert headers == { "connection": "keep-alive", "content-type": "foo/bar", "content-length": str(len(content)),
                                    "pragma": "no-cache", "cache-control": "no-cache" }, headers
                request = unpickle(content)
                assert request == { "headers": { "connection": "keep-alive", "content-length": "0",
                                                 "host": "{0[0]:s}:{0[1]:d}".format(ifc.listener_address),
                                                 "pragma": "no-cache", "cache-control": "no-cache",
                                                 "x-foo": "Override", "x-bar": "ABC"},
                                    "content": b"", "url": "/", "method": "GET" }
                assert not rc.expired

                # GET with URL and request headers

                status_code, headers, content = rc.get("/foo?%00+bar", { "X-Foo": "Bar" })
                assert status_code == 200
                assert headers == { "connection": "keep-alive", "content-type": "foo/bar", "content-length": str(len(content)),
                                    "pragma": "no-cache", "cache-control": "no-cache" }
                request = unpickle(content)
                assert request == { "headers": { "connection": "keep-alive", "content-length": "0",
                                                 "host": "{0[0]:s}:{0[1]:d}".format(ifc.listener_address),
                                                 "pragma": "no-cache", "cache-control": "no-cache", "x-foo": "Bar",
                                                 "x-bar": "ABC" },
                                    "content": b"", "url": "/foo?%00+bar", "method": "GET" }
                assert not rc.expired

                # POST with URL, request headers and content (this one is final in keep-alive sequence and is closed)

                status_code, headers, content = rc.post("/foo?%00+bar", b"\x00\x00\x00", { "X-Foo": "Bar", "CONTENT-TYPE": "zig/zag" })
                assert status_code == 200
                assert headers == { "connection": "close", "content-type": "foo/bar", "content-length": str(len(content)),
                                    "pragma": "no-cache", "cache-control": "no-cache" }
                request = unpickle(content)
                assert request == { "headers": { "connection": "close", "content-length": "3", "content-type": "zig/zag",
                                                 "host": "{0[0]:s}:{0[1]:d}".format(ifc.listener_address),
                                                 "pragma": "no-cache", "cache-control": "no-cache", "x-foo": "Bar",
                                                 "x-bar": "ABC" },
                                    "content": b"\x00\x00\x00", "url": "/foo?%00+bar", "method": "POST" }
                assert rc.expired

            finally:
                rc.disconnect()

            rc = pmnc.protocol_http.Resource("test_resource_loopback_response", **resource_config)
            rc.connect()
            try:

                # response with chunked transfer-encoding which is not supported

                with expected(Exception("transfer-encoding is not supported")):
                    rc.get("/", { "X-Response-Headers": "Transfer-Encoding=chunked" })

            finally:
                rc.disconnect()

        finally:
            ifc.cease(); ifc.stop()

    test_resource_loopback()

    ################################### TESTING RESOURCE IN TRANSACTION

    def test_resource_transaction(): # usage in transaction, this utilizes config_resource_http_1.py

        def res_transaction_pr(request, response):
            response["content"] = pickle(request)
            response["headers"]["content-type"] = "application/octet-stream"

        ifc = start_interface(res_transaction_pr)
        try:

            fake_request(3.0)

            # usage in transaction, this utilizes config_resource_http.py

            xa = pmnc.transaction.create()
            xa.http_1.post("/foo?%00+bar", b"\x00\x00\x00", { "X-Foo": "Bar", "CONTENT-TYPE": "zig/zag" })
            status_code, headers, content = xa.execute()[0]

            assert status_code == 200
            assert headers == { "connection": "keep-alive", "content-type": "application/octet-stream", "content-length": str(len(content)),
                                "pragma": "no-cache", "cache-control": "no-cache" }
            request = unpickle(content)
            assert request == { "headers": { "connection": "keep-alive", "content-length": "3", "content-type": "zig/zag",
                                             "host": "{0[0]:s}:{0[1]:d}".format(ifc.listener_address),
                                             "pragma": "no-cache", "cache-control": "no-cache", "x-foo": "Bar",
                                             "x-bar": "Def" },
                                "content": b"\x00\x00\x00", "url": "/foo?%00+bar", "method": "POST" }

            # connection is kept-alive, now try get + close

            xa = pmnc.transaction.create()
            xa.http_1.get("/foo?%00+bar", { "CONNECTION": "CLOSE" })
            status_code, headers, content = xa.execute()[0]

            assert status_code == 200
            assert headers == { "connection": "close", "content-type": "application/octet-stream", "content-length": str(len(content)),
                                "pragma": "no-cache", "cache-control": "no-cache" }

        finally:
            ifc.cease(); ifc.stop()

    test_resource_transaction()

    ################################### TESTING LOOPBACK SSL MODE

    resource_config_ssl = dict \
    (
    server_address = None, # specified in each individual test
    connect_timeout = 1.0,
    ssl_key_cert_file = os_path.join(__cage_dir__, "ssl_keys", "key_cert.pem"),
    ssl_ca_cert_file = os_path.join(__cage_dir__, "ssl_keys", "ca_cert.pem"),
    extra_headers = {},
    http_version = "HTTP/1.1",
    )

    interface_config = dict \
    (
    protocol = "http",
    listener_address = ("127.0.0.1", 0),
    max_connections = 100,
    ssl_key_cert_file = os_path.join(__cage_dir__, "ssl_keys", "key_cert.pem"),
    ssl_ca_cert_file = os_path.join(__cage_dir__, "ssl_keys", "ca_cert.pem"),
    response_encoding = "ascii",
    original_ip_header_fields = (),
    allowed_methods = ("GET", ),
    keep_alive_support = True,
    keep_alive_idle_timeout = 60.0,
    keep_alive_max_requests = 10,
    )

    def test_ssl_2way():

        def ssl_2way_pr(request, response):
            assert request["url"] == "/"
            assert pmnc.request.parameters["auth_tokens"]["encrypted"]
            assert pmnc.request.parameters["auth_tokens"]["peer_cn"] == ".*"

        ifc = start_interface(ssl_2way_pr, **interface_config)
        try:

            fake_request(3.0)

            resource_config_ssl["server_address"] = ifc.listener_address
            rc = pmnc.protocol_http.Resource("loopback_ssl", **resource_config_ssl)
            rc.connect()
            try:
                assert rc.get("/", { "X-Foo": "bar" })[0] == 200
            finally:
                rc.disconnect()

        finally:
            ifc.cease(); ifc.stop()

    test_ssl_2way()

    ###################################

    def test_ssl_1way():

        def ssl_2way_pr(request, response):
            assert request["url"] == "/"
            assert pmnc.request.parameters["auth_tokens"]["encrypted"]
            assert "peer_cn" not in pmnc.request.parameters["auth_tokens"]

        ifc = start_interface(ssl_2way_pr, **interface_config)
        try:

            fake_request(3.0)

            resource_config_ssl["server_address"] = ifc.listener_address
            resource_config_ssl["ssl_key_cert_file"] = None
            rc = pmnc.protocol_http.Resource("loopback_ssl", **resource_config_ssl)
            rc.connect()
            try:
                assert rc.get("/", { "X-Foo": "bar" })[0] == 200
            finally:
                rc.disconnect()

        finally:
            ifc.cease(); ifc.stop()

    test_ssl_1way()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
