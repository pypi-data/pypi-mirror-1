#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
###############################################################################
#
# This module contains an implementation of e-mail interface (polling over POP3)
# and resource (sending over SMTP). Technically, this code supports POP3S
# and SMTPS (same protocols but over SSL rather than plain TCP), but this is
# considered to be rare occassion and is thus not configurable (see TcpResource).
#
# Sample e-mail interface configuration (config_interface_email_1.py):
#
# config = dict \
# (
# protocol = "email",                                 # meta
# server_address = ("mail.domain.com", 110),          # tcp
# connect_timeout = 3.0,                              # tcp
# interval = 30.0,                                    # email
# username = "user",                                  # email
# password = "pass",                                  # email
# )
#
# Sample processing module (interface_email_1.py):
#
# def process_request(request, response):
#     message_id = request["message_id"]
#     message = request["message"]
#     subject = message["Subject"]
#
# Sample e-mail resource configuration (config_resource_email_1.py)
#
# config = dict \
# (
# protocol = "email",                                 # meta
# server_address = ("mail.domain.com", 25),           # tcp
# connect_timeout = 3.0,                              # tcp
# encoding = "windows-1251",                          # email
# helo = "hostname",                                  # email
# username = None,                                    # email, optional
# password = None,                                    # email, optional
# )
#
# Sample resource usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.email_1.send("From <from>", "To <to>", "subject", "message text")
# xa.email_1.send("From <from>", "To <to>", "subject", "message text",
#                 { "X-Header-Field": "Value", ... }, # optional extra header fields
#                 (("foo.jpg", "image/jpeg", b"JPEG"), ...)) # optional attachments
# xa.execute() # sending e-mail message yields no result
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource" ]

###############################################################################

import email.utils; from email.utils import parseaddr
import email.parser; from email.parser import FeedParser
import email.message; from email.message import Message
import io; from io import StringIO, BytesIO
import re; from re import compile as regex
import base64; from base64 import b64encode
import os; from os import urandom, SEEK_END
import binascii; from binascii import b2a_hex
import threading; from threading import current_thread

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck, optional, tuple_of, dict_of, by_regex, nothing, either
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource
import pmnc.threads; from pmnc.threads import HeavyThread
import pmnc.request; from pmnc.request import fake_request

###############################################################################

valid_mime_type = by_regex("^[A-Za-z0-9_-]+/[A-Za-z0-9_-]+$")

###############################################################################

class Interface: # email (POP3) interface

    @typecheck
    def __init__(self, name: str, *,
                 server_address: (str, int),
                 connect_timeout: float,
                 interval: float,
                 username: str,
                 password: str,
                 **kwargs): # this kwargs allows for extra application-specific
                            # settings in config_interface_email_X.py

        self._name = name

        if pmnc.request.self_test == __name__: # self-test harness
            self._output_queue = kwargs.pop("__output_queue")

        self._server_address = server_address
        self._connect_timeout = connect_timeout
        self._interval = interval
        self._username = username
        self._password = password

    name = property(lambda self: self._name)

    ###################################

    _content_type_charset = regex("^content-type[ \\t]*:[ \\t]*text/.*;[ \\t]*charset=\"?([A-Za-z0-9_-]+)\"?[ \\t]*(?:;|$)")
    _folded_charset = regex("^[ \\t]+charset=\"?([A-Za-z0-9_-]+)\"?[ \\t]*(?:;|$)")

    @typecheck
    def response_handler(self, data: bytes): # this callback method is invoked by
                                             # TcpResource as server response is read

        self._response.seek(0, SEEK_END)
        self._response.write(data)

        while True:

            self._response.seek(self._response_offset)

            line_b = self._response.readline()
            if line_b.endswith(b"\r\n"):
                line_b = line_b[:-2]
            elif line_b.endswith(b"\n"):
                line_b = line_b[:-1]
            else:
                return None # no complete line at the end of buffer, wait for more data

            response_offset, self._response_offset = self._response_offset, self._response.tell()

            if response_offset == 0: # first (possibly the only) line has been read
                line = line_b.decode("ascii", "replace")
                if line.startswith("+OK"):
                    if self._read_message:
                        self._message_parser = FeedParser() # proceed to message parsing
                        self._message_encoding = None
                        continue
                    else:
                        return line[3:].strip() # the successful one-line response
                elif line.startswith("-ERR"):
                    raise Exception(line[4:].strip())
                else:
                    raise Exception(line.strip())

            # hack: convert bytes to str using deduced encoding and detect encoding change

            line = line_b.decode(self._message_encoding or "ascii", "replace")

            line_lc = line.lower()
            charset_match = self._content_type_charset.match(line_lc) or \
                            self._folded_charset.match(line_lc)
            if charset_match:
                charset = charset_match.groups()[0]
                try:
                    assert b"123".decode(charset) == "123"
                except:
                    pass
                else:
                    self._message_encoding = charset

            # message lines are fed into the parser one by one

            if line != ".":
                self._message_parser.feed(line + "\r\n")
            else:
                return self._message_parser.close() # return the parsed message

    ###################################

    def _send_line(self, line: optional(str), read_message: optional(bool) = False):

        self._response = BytesIO()
        self._response_offset = 0
        self._read_message = read_message # this triggers the response_handler callback behaviour

        if line: pmnc.log.debug(">> {0:s}".format(line))
        data = line is not None and "{0:s}\r\n".format(line).encode("ascii") or b""
        response = self._pop3.send_request(data, self.response_handler)

        if not read_message:
            pmnc.log.debug("<< {0:s}".format(response))
        else:
            pmnc.log.debug("<< ...message body...")

        return response

    ###################################

    # this method is a work unit executed by one of the interface pool threads
    # if this method fails, the exception is rethrown in _process_message in wait()

    @typecheck
    def wu_process_message(self, message_id: str, message: Message) -> nothing:

        # see for how long the request was on the execution queue up to this moment
        # and whether it has expired in the meantime, if it did there is no reason
        # to proceed and we simply bail out

        if pmnc.request.expired:
            raise Exception("processing of request {0:s} was late by {1:.01f} second(s)".\
                            format(pmnc.request.unique_id, pmnc.request.expired_for))

        pending_ms = int(pmnc.request.elapsed * 1000)
        pmnc.performance.sample("interface.{0:s}.pending_time".\
                                format(self._name), pending_ms)

        request = dict(message_id = message_id, message = message)
        response = dict()

        with pmnc.performance.timing("interface.{0:s}.processing_time".\
                                     format(self._name)):

            if pmnc.request.self_test == __name__: # self-test harness
                if "SELF_TEST_ERROR" in request["message"]:
                    raise Exception(request["message"]["SELF_TEST_ERROR"])
                else:
                    self._output_queue.push(request)
            else: # default behaviour is to invoke the application handler
                handler_module_name = "interface_{0:s}".format(self._name)
                pmnc.__getattr__(handler_module_name).process_request(request, response)

    ###################################

    # request processing in a message-oriented interface is rather straightforward

    def _process_message(self, message_id: str):

        # note that the time spent in POP3 message retrieval is deducted
        # from the request processing time (because we can do so)
        # also note that the deadlines for both requests are now identical

        request_parameters = dict(auth_tokens = dict(mailbox = self._username))
        request = pmnc.interfaces.begin_request(timeout = pmnc.request.remain,
                                                interface = self._name,
                                                protocol = "email",
                                                parameters = request_parameters)
        try:

            pmnc.log.info("mailbox {0:s}@{1:s} via interface {2:s} introduces request {3:s} for "
                          "processing e-mail message {4:s}, deadline in {5:.01f} second(s)".\
                          format(self._username, self._server_address[0], self._name,
                                 request.unique_id, message_id, request.remain))

            pmnc.performance.event("interface.{0:s}.request_rate".format(self._name))
            try:

                try:

                    start = pmnc.request.elapsed
                    try:

                        # receive the message contents, the time spent receiving
                        # is therefore deducted from the processing time

                        try:
                            message = self._send_line("RETR 1", True)
                            pmnc.interfaces.enqueue(request, self.wu_process_message,
                                                    (message_id, message)).wait()
                        except:
                            pmnc.log.error("processing of e-mail message {0:s} has failed: {1:s}".\
                                           format(message_id, exc_string()))
                            raise
                        else:
                            pmnc.log.info("processing of e-mail message {0:s} has succeeded".\
                                          format(message_id))

                        # sending DELE + QUIT is mandatory for successful message
                        # processing from the server point of view, if the following
                        # two commands fail, the message is gonna be processed again

                        try:
                            self._send_line("DELE 1")
                            self._send_line("QUIT")
                        except:
                            pmnc.log.error(exc_string()) # to have the error logged
                            raise

                    finally:
                        elapsed_sec = pmnc.request.elapsed - start
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
            else:
                pmnc.performance.sample("interface.{0:s}.response_time.success".\
                                        format(self._name), elapsed_ms)
                pmnc.performance.event("interface.{0:s}.response_rate.success".\
                                       format(self._name))

        finally:

            # although the request may still be pending for execution,
            # there is need to wait for it any more

            pmnc.interfaces.end_request(request)

    ###################################

    # this thread periodically polls the mail server for new messages

    def _poller_proc(self):

        poll_interval = self._interval

        while not current_thread().stopped(poll_interval):
            try:

                # attach a new fake request to this thread so that
                # network access in TcpResource times out properly

                fake_request(timeout = pmnc.config_interfaces.get("request_timeout"))

                # establish a new connection to the POP3 server

                self._pop3 = \
                    pmnc.protocol_tcp.TcpResource(self._username,
                                                  server_address = self._server_address,
                                                  connect_timeout = self._connect_timeout,
                                                  ssl_key_cert_file = None, # technically this code
                                                  ssl_ca_cert_file = None)  # supports POP3 over SSL
                self._pop3.connect()
                try:

                    # go through the login phase

                    self._send_line(None)
                    self._send_line("USER {0:s}".format(self._username))
                    self._send_line("PASS {0:s}".format(self._password))

                    # see if there are messages at all

                    stat = self._send_line("STAT")
                    message_count = int(stat.split(" ")[0])
                    poll_interval = message_count <= 1 and self._interval or 0.0
                    if message_count == 0:
                        self._send_line("QUIT")
                        continue

                    # since there is no other way to commit POP3 receiving transaction
                    # but to disconnect, we have to limit each session to one message

                    uidl = self._send_line("UIDL 1")
                    message_id = uidl.split(" ")[1]

                    # receive and process the message

                    self._process_message(message_id)

                finally:
                    self._pop3.disconnect()

            except:
                pmnc.log.error(exc_string())
                poll_interval = self._interval # this prevents full-speed failure looping

    ###################################

    # to start/stop an interface the poller thread is started/stopped

    def start(self):

        self._poller = HeavyThread(target = self._poller_proc,
                                   name = "{0:s}:poll".format(self._name))
        self._poller.start()

    def cease(self):

        self._poller.stop()

    def stop(self):

        pass

###############################################################################

class Resource(TransactionalResource): # email (SMTP) resource

    @typecheck
    def __init__(self, name: str, *,
                 server_address: (str, int),
                 connect_timeout: float,
                 encoding: str,
                 helo: str,
                 username: optional(str),
                 password: optional(str)):

        TransactionalResource.__init__(self, name)

        self._tcp_resource = \
            pmnc.protocol_tcp.TcpResource(name,
                                          server_address = server_address,
                                          connect_timeout = connect_timeout,
                                          ssl_key_cert_file = None, # technically this code
                                          ssl_ca_cert_file = None)  # supports SMTP over SSL
        self._encoding, self._b_encoding = encoding, encoding.encode("ascii")
        self._helo, self._username, self._password = helo, username, password

    ###################################

    _response_line_parser = regex("^([0-9]+)([ -])(.*)$")

    # this callback method is invoked by TcpResource as server response is read

    @typecheck
    def response_handler(self, data: bytes) -> optional((int, str)):

        self._response.seek(0, SEEK_END)
        self._response.write(data.decode("ascii", "replace"))

        while True: # SMTP response can consist of multiple lines

            self._response.seek(self._response_offset)
            line = self._response.readline()

            if line.endswith("\r\n"):
                line = line[:-2]
            elif line.endswith("\n"):
                line = line[:-1]
            else:
                return None # no complete line at the end of buffer

            self._response_offset = self._response.tell()

            try:
                retcode, delim, message = \
                    self._response_line_parser.findall(line)[0]
            except:
                raise Exception("invalid server response: {0:s}".format(line))

            if delim == " ": # this is the last line of the response
                return int(retcode), message

    ################################### NETWORK-RELATED METHODS

    def _send_bytes(self, data: bytes, positive_retcodes: tuple_of(int)):

        self._response = StringIO() # SMTP server responses are treated as ascii-only
        self._response_offset = 0

        if positive_retcodes:
            retcode, message = self._tcp_resource.send_request(data, self.response_handler)
            pmnc.log.debug("<< {0:d} {1:s}".format(retcode, message))
            if retcode not in positive_retcodes:
                raise Exception("server response {0:d}: {1:s}".format(retcode, message))
        else:
            self._tcp_resource.send_request(data)

    ###################################

    def _send_line(self, line: optional(str), positive_retcodes: tuple_of(int)):

        if line: pmnc.log.debug(">> {0:s}".format(line))
        data = line is not None and "{0:s}\r\n".format(line).encode("ascii") or b""
        self._send_bytes(data, positive_retcodes)

    ################################### MESSAGE-FORMATTING METHODS

    def _wrap_value(self, s):
        try:
            return s.encode("ascii")
        except:
            return b"=?" + self._b_encoding + b"?B?" + b64encode(s.encode(self._encoding)) + b"?="

    ###################################

    def _wrap_addr(self, addr: str) -> bytes:

        name, addr = parseaddr(addr)
        if name:
            return addr, self._wrap_value(name) + b" <" + addr.encode("ascii") + b">"
        else:
            return addr, addr.encode("ascii")

    ###################################

    def _wrap_part(self, headers: dict_of(str, str), content: bytes) -> bytes:

        result = BytesIO()

        headers["Content-Transfer-Encoding"] = "base64"
        for k, v in headers.items():
            result.write(k.encode("ascii") + b": " + v.encode("ascii") + b"\r\n")
        result.write(b"\r\n")

        content = BytesIO(content)
        raw_line = content.read(57)
        while raw_line:
            result.write(b64encode(raw_line) + b"\r\n")
            raw_line = content.read(57)

        return result.getvalue()

    ###################################

    def _wrap_text(self, text: str) -> bytes:

        return self._wrap_part({ "Content-Type": "text/plain; charset={0:s}".format(self._encoding),
                                 "Content-Disposition": "inline" },
                               text.encode(self._encoding))

    ###################################

    def _wrap_attachment(self, filename: str, mime_type: str, data: bytes) -> bytes:

        filename = self._wrap_value(filename).decode("ascii")
        return self._wrap_part({ "Content-Type": mime_type,
                                 "Content-Disposition": "attachment; filename={0:s}".format(filename) },
                               data)

    ###################################

    def make_boundary(self) -> bytes:

        return b2a_hex(urandom(16))

    ###################################

    @typecheck
    def _wrap_message(self, from_name: bytes, to_name: bytes, subject: str, text: str, headers: dict_of(str, str),
                      attachments: tuple_of((str, str, either(str, bytes)))) -> bytes:

        result = BytesIO()

        boundary = self.make_boundary() # this random boundary separates message parts (ex. attachments)

        # email-specific fields are contained in the outer envelope

        result.write(b"MIME-Version: 1.0\r\n" \
                     b"Content-Type: multipart/mixed; boundary=\"" + boundary + b"\"\r\n" \
                     b"From: " + from_name + b"\r\n" \
                     b"To: " + to_name + b"\r\n" \
                     b"Subject: " + self._wrap_value(subject) + b"\r\n" \
                     b"X-Transaction-ID: " + self.xid.encode("ascii") + b"\r\n")

        # append user-defined header fields

        for k, v in headers.items():
            result.write(k.encode("ascii") + b": " + v.encode("ascii") + b"\r\n")

        # append textual body

        result.write(b"\r\n--" + boundary + b"\r\n" +
                     self._wrap_text(text))

        # append attachments

        for filename, mime_type, content in attachments:
            if mime_type.startswith("text/"):
                assert isinstance(content, str), "attachment of type text/* should be str"
                content = content.encode(self._encoding)
                mime_type += "; charset={0:s}".format(self._encoding)
            else:
                assert isinstance(content, bytes), "attachment not of type text/* should be bytes"
            result.write(b"--" + boundary + b"\r\n" +
                         self._wrap_attachment(filename, mime_type, content))

        # complete the message and return the entire stream contents

        result.write(b"--" + boundary + b"--\r\n")

        return result.getvalue()

    ###################################

    def connect(self):

        self._tcp_resource.connect()
        self._send_line(None, (220, ))
        self._send_line("HELO {0:s}".format(self._helo), (250, ))
        if self._username and self._password:
            self._send_line("AUTH PLAIN {0:s}".format(self._make_auth_plain()), (235, ))
        self._graceful_close = True

        TransactionalResource.connect(self)

    ###################################

    def _make_auth_plain(self):

        return b64encode(b"\x00" + self._username.encode("ascii") +
                         b"\x00" + self._password.encode("ascii")).decode("ascii")

    ###################################

    def disconnect(self):
        try:
            try:
                if self._graceful_close:
                    self._send_line("QUIT", (221, ))
            finally:
                self._tcp_resource.disconnect()
        except:
            pmnc.log.error(exc_string()) # log and ignore

        TransactionalResource.disconnect(self)

    ###################################

    @typecheck
    def send(self, from_addr: str, to_addr: str, subject: str, text: str,
             headers: optional(dict_of(str, str)) = None,
             attachments: optional(tuple_of((str, valid_mime_type, either(str, bytes)))) = None):

        from_addr, from_name = self._wrap_addr(from_addr) # addresses may possibly contain international
        to_addr, to_name = self._wrap_addr(to_addr)       # characters and need to be wrapped

        message_data = self._wrap_message(from_name, to_name, subject, text,
                                          headers or {}, attachments or ())

        pmnc.log.info("sending e-mail message to {0:s}: {1:d} byte(s)".\
                      format(to_addr, len(message_data)))
        try:

            self._send_line("MAIL FROM:<{0:s}>".format(from_addr), (250, ))
            self._send_line("RCPT TO:<{0:s}>".format(to_addr), (250, ))
            self._send_line("DATA", (354, ))

            pmnc.log.debug(">> ...message body...")
            self._send_bytes(message_data, ())

        except:
            pmnc.log.error("e-mail message has not been sent: {0:s}".format(exc_string()))
            raise
        else:
            pmnc.log.info("e-mail message has been sent")

    ###################################

    def commit(self):
        self._send_line(".", (250, ))
        pmnc.log.info("e-mail message has been committed")

    ###################################

    def rollback(self):
        self._graceful_close = False
        self.expire() # connection is silently dropped at disconnect
        pmnc.log.info("e-mail message has been rolled back")

###############################################################################

def self_test():

    from expected import expected
    from time import sleep
    from interlocked_queue import InterlockedQueue
    from email.header import decode_header

    russian = "\u0410\u0411\u0412\u0413\u0414\u0415\u0401\u0416\u0417\u0418\u0419\u041a" \
              "\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424\u0425\u0426" \
              "\u0427\u0428\u0429\u042c\u042b\u042a\u042d\u042e\u042f\u0430\u0431\u0432" \
              "\u0433\u0434\u0435\u0451\u0436\u0437\u0438\u0439\u043a\u043b\u043c\u043d" \
              "\u043e\u043f\u0440\u0441\u0442\u0443\u0444\u0445\u0446\u0447\u0448\u0449" \
              "\u044c\u044b\u044a\u044d\u044e\u044f"

    ###################################

    def test_resource_wrap_value():

        r = Resource("test_resource_wrap_value", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "windows-1251", helo = "test",
                     username = None, password = None)

        assert r._wrap_value("foo@bar") == b"foo@bar"
        assert r._wrap_value(russian) == b"=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva" \
                                         b"3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?="

        r = Resource("test_resource_wrap_value", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "cp866", helo = "test",
                     username = None, password = None)

        assert r._wrap_value("foo@bar") == b"foo@bar"
        assert r._wrap_value(russian) == b"=?cp866?B?gIGCg4SF8IaHiImKi4yNjo+QkZKTlJWWl5iZnJuan" \
                                         b"Z6foKGio6Sl8aanqKmqq6ytrq/g4eLj5OXm5+jp7Ovq7e7v?="

    test_resource_wrap_value()

    ###################################

    def test_resource_wrap_addr():

        r = Resource("test_resource_wrap_addr", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "windows-1251", helo = "test",
                     username = None, password = None)

        assert r._wrap_addr("foo@bar") == ("foo@bar", b"foo@bar")
        assert r._wrap_addr("foobar <foo@bar>") == ("foo@bar", b"foobar <foo@bar>")
        assert r._wrap_addr(russian + " <foo@bar>") == ("foo@bar", b"=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4O" \
                                                                   b"Hi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?= <foo@bar>")
        with expected(UnicodeEncodeError):
            r._wrap_addr(russian + " <" + russian + ">")

    test_resource_wrap_addr()

    ###################################

    def test_resource_wrap_part():

        r = Resource("test_resource_wrap_part", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "windows-1251", helo = "test",
                     username = None, password = None)

        assert r._wrap_part({ "X-Foo": "Bar", "X-Biz": "baz" }, b"data") == \
               b"Content-Transfer-Encoding: base64\r\nX-Biz: baz\r\nX-Foo: Bar\r\n\r\nZGF0YQ==\r\n"

        assert r._wrap_part({ "X-Foo": "Bar", "X-Biz": "baz" }, b"data" * 20) == \
               b"Content-Transfer-Encoding: base64\r\nX-Biz: baz\r\nX-Foo: Bar\r\n\r\n" \
               b"ZGF0YWRhdGFkYXRhZGF0YWRhdGFkYXRhZGF0YWRhdGFkYXRhZGF0YWRhdGFkYXRhZGF0YWRhdGFk\r\n" \
               b"YXRhZGF0YWRhdGFkYXRhZGF0YWRhdGE=\r\n"

        with expected(UnicodeEncodeError):
            r._wrap_part({ "X-Foo": russian }, b"")

        with expected(UnicodeEncodeError):
            r._wrap_part({ russian: "Bar" }, b"")

    test_resource_wrap_part()

    ###################################

    def test_resource_wrap_text():

        r = Resource("test_resource_wrap_text", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "windows-1251", helo = "test",
                     username = None, password = None)

        assert r._wrap_text("foo") == \
               b"Content-Transfer-Encoding: base64\r\nContent-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n\r\nZm9v\r\n"

        assert r._wrap_text(russian) == \
               b"Content-Transfer-Encoding: base64\r\nContent-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n\r\n" \
               b"wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX2\r\n9/j5/Pv6/f7/\r\n"

    test_resource_wrap_text()

    ###################################

    def test_resource_wrap_attachment():

        r = Resource("test_resource_wrap_attachment", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "windows-1251", helo = "test",
                     username = None, password = None)

        assert r._wrap_attachment("foo.jpg", "image/jpeg", b"JPEG") == \
               b"Content-Transfer-Encoding: base64\r\nContent-Type: image/jpeg\r\n" \
               b"Content-Disposition: attachment; filename=foo.jpg\r\n\r\nSlBFRw==\r\n"

    test_resource_wrap_attachment()

    ###################################

    # utility function

    begin_transaction = \
        lambda r: r.begin_transaction("xid", source_module_name = __name__,
                                      transaction_options = {}, resource_args = (),
                                      resource_kwargs = {})

    def test_resource_wrap_message():

        r = Resource("test_resource_wrap_message", server_address = ("", 0),
                     connect_timeout = 1.0, encoding = "windows-1251", helo = "test",
                     username = None, password = None)

        begin_transaction(r)

        r.make_boundary = lambda: b"abcdef" # test-only hack

        assert r._wrap_message(b"from@host", b"to@host", "subject", "text", {}, ()) == \
               b"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=\"abcdef\"\r\n" \
               b"From: from@host\r\nTo: to@host\r\nSubject: subject\r\nX-Transaction-ID: xid\r\n\r\n" \
               b"--abcdef\r\nContent-Transfer-Encoding: base64\r\nContent-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n\r\ndGV4dA==\r\n--abcdef--\r\n"

        assert r._wrap_message(b"from@host", b"to@host", "", "", { "X-Foo": "bar" }, ()) == \
               b"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=\"abcdef\"\r\n" \
               b"From: from@host\r\nTo: to@host\r\nSubject: \r\nX-Transaction-ID: xid\r\nX-Foo: bar\r\n\r\n" \
               b"--abcdef\r\nContent-Transfer-Encoding: base64\r\nContent-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n\r\n--abcdef--\r\n"

        assert r._wrap_message(b"from@host", b"to@host", russian, russian, {},
                               (("foo.jpg", "image/jpeg", b"JPEG"), ("foo.txt", "text/plain", "TEXT"))) == \
               b"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=\"abcdef\"\r\n" \
               b"From: from@host\r\nTo: to@host\r\nSubject: =?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4OHi4" \
               b"+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?=\r\nX-Transaction-ID: xid\r\n\r\n--abcdef\r\n" \
               b"Content-Transfer-Encoding: base64\r\nContent-Type: text/plain; charset=windows-1251\r\n" \
               b"Content-Disposition: inline\r\n\r\nwMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4OHi4+TluObn6Onq6+zt7u" \
               b"/w8fLz9PX2\r\n9/j5/Pv6/f7/\r\n--abcdef\r\nContent-Transfer-Encoding: base64\r\nContent-Type: image/jpeg\r\n" \
               b"Content-Disposition: attachment; filename=foo.jpg\r\n\r\nSlBFRw==\r\n--abcdef\r\nContent-Transfer-Encoding: base64\r\n" \
               b"Content-Type: text/plain; charset=windows-1251\r\nContent-Disposition: attachment; filename=foo.txt\r\n\r\n" \
               b"VEVYVA==\r\n--abcdef--\r\n"

    test_resource_wrap_message()

    ###################################

    from_addr = "test2@domain.com"
    to_addr = "test1@domain.com"

    ###################################

    def start_interface(output_queue):

        config = pmnc.config_interface_email_1.copy()
        ifc = pmnc.interface.create("email_1", __output_queue = output_queue, **config)
        ifc.start()
        return ifc

    ###################################

    def drain_mailbox():

        incoming_messages = InterlockedQueue()

        ifc = start_interface(incoming_messages)
        try:
            try:
                while incoming_messages.pop(10.0) is not None:
                    pass
            finally:
                ifc.cease()
        finally:
            ifc.stop()

    drain_mailbox()

    ###################################

    def test_loopback_interface():

        incoming_messages = InterlockedQueue()

        ifc = start_interface(incoming_messages)
        try:
            try:

                fake_request(30.0)

                # send two messages in the same transaction,
                # one with attachment and one without

                xa = pmnc.transaction.create()
                xa.email_1.send("\u0414\u0432\u043e\u0439\u043d\u0438\u043a\u043e\u0432 \u0414\u043c\u0438\u0442\u0440\u0438\u0439\u0412\u0430\u043b\u0435\u043d\u0442\u0438\u043d\u043e\u0432\u0438\u0447 <{0:s}>".format(from_addr),
                                to_addr, "\u0442\u0435\u0441\u04421", "\u0422\u0415\u0421\u04221")
                xa.email_1.send(from_addr,
                                "\u0424\u0438\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u044f\u0449\u0438\u043a <{0:s}>".format(to_addr),
                                "\u0442\u0435\u0441\u04422", "\u0422\u0415\u0421\u04222\r\n" * 1000, { "X-Foo": "bar" },
                                ((russian, "text/plain", russian),
                                 ("bar.jpg", "image/jpeg", b"\x00\x00\x00")))
                assert xa.execute() == (None, None)

                # receive the messages and parse them

                def decode_field(s):
                    decoded = decode_header(s)
                    assert len(decoded) == 1
                    name, charset = decoded[0]
                    return (name or b"").decode(charset or "ascii")

                def decode_addr(s):
                    addr = parseaddr(s)
                    return decode_field(addr[0]), addr[1]

                def decode_content(m):
                    assert not m.is_multipart()
                    if m.get_filename():
                        if m.get_content_maintype() == "text":
                            return m.get_filename(), m.get_payload(decode = True).decode(m.get_content_charset("ascii"))
                        else:
                            return m.get_filename(), m.get_content_type(), m.get_payload(decode = True)
                    else:
                        if m.get_content_maintype() == "text":
                            return m.get_payload(decode = True).decode(m.get_content_charset("ascii"))
                        else:
                            return m.get_content_type(), m.get_payload(decode = True)

                # the order in which the messages are received is not determined

                m1 = incoming_messages.pop(30.0)["message"]
                m2 = incoming_messages.pop(30.0)["message"]

                if decode_field(m2["subject"]) == "\u0442\u0435\u0441\u04421":
                    m1, m2 = m2, m1

                # a message without attachment

                assert decode_addr(m1["From"]) == ("\u0414\u0432\u043e\u0439\u043d\u0438\u043a\u043e\u0432 \u0414\u043c\u0438\u0442\u0440\u0438\u0439\u0412\u0430\u043b\u0435\u043d\u0442\u0438\u043d\u043e\u0432\u0438\u0447", from_addr)
                assert decode_addr(m1["To"]) == ("", to_addr)
                assert decode_field(m1["Subject"]) == "\u0442\u0435\u0441\u04421"

                m1p = [ decode_content(m) for m in m1.walk() if not m.is_multipart() ]
                assert m1p == [ "\u0422\u0415\u0421\u04221" ]

                # a message with attachment

                assert decode_addr(m2["From"]) == ("", from_addr)
                assert decode_addr(m2["To"]) == ("\u0424\u0438\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u044f\u0449\u0438\u043a", to_addr)
                assert decode_field(m2["Subject"]) == "\u0442\u0435\u0441\u04422"

                m2p = [ decode_content(m) for m in m2.walk() if not m.is_multipart() ]
                assert len(m2p) == 3
                assert m2p[0] == "\u0422\u0415\u0421\u04222\r\n" * 1000
                assert m2p[1] == ("=?windows-1251?B?wMHCw8TFqMbHyMnKy8zNzs/Q0dLT1NXW19jZ3Nva3d7f4OHi4+TluObn6Onq6+zt7u/w8fLz9PX29/j5/Pv6/f7/?=", russian)
                assert m2p[2] == ("bar.jpg", "image/jpeg", b"\x00\x00\x00")

                # see that rollback causes the message to not be delivered

                xa = pmnc.transaction.create()
                xa.email_1.send(from_addr, to_addr,
                                "\u0442\u0435\u0441\u0442", "\u0422\u0415\u0421\u0422")
                xa.state.set("should deadlock", "bar") # this attempt to set the same value
                xa.state.set("should deadlock", "biz") # causes deadlock and rollback
                with expected(Exception("request deadline waiting for intermediate results")):
                    xa.execute()

                assert incoming_messages.pop(10.0) is None

            finally:
                ifc.cease()
        finally:
            ifc.stop()

    test_loopback_interface()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
