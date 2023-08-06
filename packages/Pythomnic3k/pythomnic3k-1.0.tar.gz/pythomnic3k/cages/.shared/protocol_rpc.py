#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
###############################################################################
#
# This module contains implementation of an RPC interface and resource, built
# on top of TcpInterface/TcpResource. Pythomnic3k RPC is based on the following
# principles:
#
# 1. Automatic discovery of a target cage. Whenever some cage executes
#    pmnc("othercage").module.method(...)
#    the location of othercage is discovered automatically and transparently
#    by sending out UDP broadcasts to which (either copy of) othercage presumably
#    responds. The received response contains the listening address of the
#    responded cage and TCP/SSL connection can be initiated.
#
# 2. Multiple cages with the same name can be running on different servers,
#    they all respond to the discovery requests. One of the responses to arrive
#    first is chosen, and responses from different cages may cause connections
#    to different copies of the target cage to exist at the same time.
#
# 3. Hence this - in Pythomnic3k there is no difference between copies of
#    identically named cages - they are supposed to be freely interchangeable.
#    This fact is stressed by using SSL certificates to authenticate cages
#    to each other - each "cage" presumably owns a certificate which has common
#    name of "cage". This allows cages to trust each other at least by name.
#
# 4. RPC implemented here is synchronous and plays by Pythomnic3k rules of non-
#    blocking and timing out within deadline. Execution of the call on the target
#    cage inherits the original timeout, therefore the original request is logically
#    "extended" to the target cage and impersonated for the course of RPC execution.
#
# 5. Each cage advertises its location by periodically sending out broadast
#    requests. The received locations of other cages are kept on record and
#    can be accessed by get_cages and get_nodes methods of the rpc interface,
#    this is used by the health_monitor cage to locate active cages.
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Interface", "Resource", "Handler", "self_test_loopback" ]

###############################################################################

import os; from os import urandom, SEEK_SET, SEEK_CUR, SEEK_END, path as os_path
import time; from time import time
import binascii; from binascii import b2a_hex
import select; from select import select
import io; from io import BytesIO
import hashlib; from hashlib import sha1
import threading; from threading import current_thread, Lock
import pickle; from pickle import load as unpickle, dumps as pickles
import random; from random import randint
import ssl; from ssl import CERT_REQUIRED
import socket; from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, \
                                  SO_BROADCAST, SO_REUSEADDR, error as socket_error
try:
    from socket import SO_REUSEPORT
except ImportError:
    have_reuse_port = False
else:
    have_reuse_port = True

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck, optional, by_regex, dict_of
import pmnc.resource_pool; from pmnc.resource_pool import TransactionalResource
import pmnc.timeout; from pmnc.timeout import Timeout
import pmnc.threads; from pmnc.threads import HeavyThread

###############################################################################

valid_cage_name = by_regex("^[A-Za-z0-9_-]{1,32}$")
valid_node_name = by_regex("^[A-Za-z0-9_-]{1,32}$")
valid_flock_id = by_regex("^[A-Za-z0-9_-]+$")
valid_location = by_regex("^(ssl|tcp)://([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|\\*):[0-9]{1,5}/$")
valid_exact_location = by_regex("^(ssl|tcp)://[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}:[0-9]{1,5}/$")

###############################################################################

def _get_peer_name(ssl_socket):
    for f in ssl_socket.getpeercert()["subject"]:
        if f[0][0] == "commonName":
            return f[0][1]
    else:
        return None

###############################################################################

def _create_sending_broadcast_socket(addr: str) -> socket:
    bc_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        bc_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        bc_socket.bind((addr, 0))
    except:
        bc_socket.close()
        raise
    else:
        return bc_socket

###############################################################################

def _create_receiving_broadcast_socket(port: int) -> socket:
    bc_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        bc_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        if have_reuse_port:
            bc_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        bc_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        bc_socket.bind(("0.0.0.0", port))
    except:
        bc_socket.close()
        raise
    else:
        return bc_socket

###############################################################################

# key files required to establish SSL connection
# may reside in current cage or in .shared

def _locate_key_file(filename: str) -> optional(os_path.isfile):

    s = os_path.join(__cage_dir__, "ssl_keys", filename)
    if os_path.isfile(s):
        return s

    s = os_path.normpath(os_path.join(__cage_dir__, "..", ".shared", "ssl_keys", filename))
    if os_path.isfile(s):
        return s

    return None

###############################################################################

class RpcPacket():

    def __init__(self, max_size: optional(int) = 2**32):
        self._max_size = max_size
        self._stream = BytesIO()
        self._length = None
        self._expected_hash = None
        self._running_hash = None
        self._method = None

    @staticmethod
    def marshal(data):
        return b"PKL3" + pickles(data)

    def _unmarshal(self):
        if self._method == "PKL3":
            self._stream.seek(52, SEEK_SET)
            return unpickle(self._stream)
        else:
            raise Exception("unsupported marshaling method: "
                            "{0:s}".format(self._method))

    def write(self, data: bytes):

        self._stream.write(data)
        if self._stream.tell() > self._max_size:
            raise Exception("packet size exceeded")

        if self._length is None and self._stream.tell() >= 8:
            self._stream.seek(0, SEEK_SET)
            self._length = int(self._stream.read(8).decode("ascii"), 16) + 48
            if self._length > self._max_size:
                raise Exception("request size exceeded")
            self._stream.seek(0, SEEK_END)

        if self._expected_hash is None and self._stream.tell() >= 48:
            self._stream.seek(8, SEEK_SET)
            self._expected_hash = self._stream.read(40).decode("ascii")
            self._running_hash = sha1(self._stream.read())
        elif self._running_hash is not None:
            self._running_hash.update(data)

        if self._method is None and self._stream.tell() >= 52:
            self._stream.seek(48, SEEK_SET)
            self._method = self._stream.read(4).decode("ascii")
            self._stream.seek(0, SEEK_END)

        if self._stream.tell() == self._length:
            if self._running_hash.hexdigest().upper() != self._expected_hash:
                raise Exception("request hash mismatch")
            return self._unmarshal()
        else:
            return None

###############################################################################

class Interface: # RPC interface

    _ad_periods = (10.0, 20.0, 30.0, 60.0, 180.0, 300.0, 600.0) # the last one is repeated

    @typecheck
    def __init__(self, name: str, *,
                 random_port: lambda i: isinstance(i, int) and (-65500 <= i <= 65535),
                 max_connections: int,
                 broadcast_address: (str, int),
                 flock_id: valid_flock_id,
                 separate_thread_pool: optional(bool) = False,
                 disable_broadcast: optional(bool) = False):

        self._name = name
        broadcast_address, self._broadcast_port = broadcast_address
        self._bind_address, self._broadcast_address = broadcast_address.split("/")
        self._flock_id = flock_id
        self._disable_broadcast = disable_broadcast
        self._request_prefix = "PYTHOMNIC3K-REQUEST:{0:s}:".format(flock_id)
        self._response_prefix = "PYTHOMNIC3K-RESPONSE:{0:s}:".format(flock_id)
        self._known_cages = {} # { cage: { node: { location: ..., expires_at: ... } } }
        self._known_cages_lock = Lock()
        self._ad_period_idx = 0
        self._cage_name = __cage__ # makes it possible to override in self-tests

        ssl_key_cert_file = _locate_key_file("key_cert.pem")
        ssl_ca_cert_file = _locate_key_file("ca_cert.pem")

        # having handler factory create handlers through a pmnc call
        # allows online modifications to this module, after it is reloaded

        handler_factory = lambda prev_handler: pmnc.protocol_rpc.Handler(prev_handler, self._cage_name)

        # create an instance of underlying TCP interface, note that in case
        # of SSL we require the client (source cage) to present a certificate

        self._tcp_interface = \
            pmnc.protocol_tcp.TcpInterface(name, handler_factory,
                                           listener_address = (self._bind_address, random_port),
                                           max_connections = max_connections,
                                           ssl_key_cert_file = ssl_key_cert_file,
                                           ssl_ca_cert_file = ssl_ca_cert_file,
                                           required_auth_level = CERT_REQUIRED)
        if separate_thread_pool:
            self._thread_pool = pmnc.shared_pools.get_private_thread_pool()
            self._tcp_interface._enqueue_request = self._enqueue_request

    name = property(lambda self: self._tcp_interface.name)
    listener_address = property(lambda self: self._tcp_interface.listener_address)

    ###################################

    def _enqueue_request(self, *args, **kwargs):

        self._thread_pool.enqueue(*args, **kwargs)

    ###################################

    def start(self):

        # start the underlying TCP interface

        self._tcp_interface.start()

        # create and start broadcaster thread

        if not self._disable_broadcast:
            self._broadcaster = HeavyThread(target = self._broadcaster_proc,
                                            name = "{0:s}:brc".format(self._name))
            self._broadcaster.start()

    ###################################

    def cease(self):

        if not self._disable_broadcast:
            self._broadcaster.stop()

        self._tcp_interface.cease()

    ###################################

    def stop(self):

        self._tcp_interface.stop()

    ###################################

    def get_cages(self):

        with self._known_cages_lock:
            return set(self._known_cages.keys())

    ###################################

    @typecheck
    def get_nodes(self, cage: valid_cage_name):

        with self._known_cages_lock:
            nodes = self._known_cages.get(cage, {})
            return { node: cage_info["location"]
                     for node, cage_info in nodes.items() }

    ###################################

    def _discovery_response(self, request_id: str) -> bytes:

        return "{0:s}{1:s}:{2:s}://*:{3:d}/".\
               format(self._response_prefix, request_id,
                      self._tcp_interface.encrypted and "ssl" or "tcp",
                      self._tcp_interface.listener_address[1]).\
               encode("ascii")

    ###################################

    def _next_advertisement_timeout(self) -> Timeout:

        ad_period = self._ad_periods[self._ad_period_idx]
        if self._ad_period_idx < len(self._ad_periods) - 1:
            self._ad_period_idx += 1
        return Timeout(ad_period)

    ###################################

    def _advertisement_packet(self) -> bytes:

        request_id = b2a_hex(urandom(8)).decode("ascii").upper()
        return "{0:s}{1:s}:ADVERTISE-CAGE:{2:s}:{3:s}:{4:d}:{5:s}://*:{6:d}/".\
               format(self._request_prefix, request_id, __node__,
                      self._cage_name, int(self._ad_periods[self._ad_period_idx]),
                      self._tcp_interface.encrypted and "ssl" or "tcp",
                      self._tcp_interface.listener_address[1]).\
               encode("ascii")

    ###################################

    def _broadcast_advertisement(self):

        bc_socket = _create_sending_broadcast_socket(self._bind_address)
        try:
            pmnc.log.debug("broadcasting cage advertisement: {0:s}.{1:s} is at {2:s}://*:{3:d}/".\
                           format(__node__, self._cage_name, self._tcp_interface.encrypted and "ssl" or "tcp",
                                  self._tcp_interface.listener_address[1]))
            bc_socket.sendto(self._advertisement_packet(), (self._broadcast_address, self._broadcast_port))
        finally:
            bc_socket.close()

    ###################################

    def _handle_received_packet(self, packet: str, client_addr: str, client_port: int):

        if not packet.startswith(self._request_prefix):
            return

        request_id, request, request_params = packet[len(self._request_prefix):].split(":", 2)

        if request == "DISCOVER-CAGE":

            if request_params == self._cage_name:
                discovery_response = self._discovery_response(request_id)
                pmnc.log.debug("sending response to discovery request "
                               "from {0:s}".format(client_addr))
                self._bc_socket.sendto(discovery_response, (client_addr, client_port))

        elif request == "ADVERTISE-CAGE":

            node, cage, period, advertised_location = request_params.split(":", 3)
            try:
                period = int(period)
            except ValueError:
                period = 0

            if valid_cage_name(cage) and valid_node_name(node) and \
               1 <= period <= 3600 and valid_location(advertised_location):

                cage_addr, cage_port = advertised_location[6:-1].split(":")
                if cage_addr == "*": cage_addr = client_addr
                location = "{0:s}{1:s}:{2:s}/".format(advertised_location[:6],
                                                      cage_addr, cage_port)

                with self._known_cages_lock:
                    nodes = self._known_cages.setdefault(cage, {})
                    if nodes.get(node, {}).get("location") != location:
                        pmnc.log.debug("received cage advertisement: {0:s}.{1:s} "
                                       "is at {2:s}".format(node, cage, location))
                    nodes[node] = dict(location = location, expires_at = time() + period * 2)

    ###################################

    def _purge_known_cages(self):

        purge_time = time()
        with self._known_cages_lock:
            for cage, nodes in self._known_cages.items():
                expired_nodes = [ node for node, cage_info in nodes.items()
                                  if cage_info["expires_at"]  < purge_time ]
                for expired_node in expired_nodes:
                    del nodes[expired_node]

    ###################################

    def _broadcaster_proc(self):
        try:

            # the listening socket must be bound to the configured port

            self._bc_socket = _create_receiving_broadcast_socket(self._broadcast_port)
            try:

                ad_timeout = self._next_advertisement_timeout()

                while not current_thread().stopped(): # lifetime loop
                    try:

                        # receive incoming broadcast packets

                        receive_timeout = Timeout(1.0)
                        while not receive_timeout.expired and select([self._bc_socket], [], [], receive_timeout.remain)[0]:
                            try:
                                try:
                                    packet, (client_addr, client_port) = self._bc_socket.recvfrom(57344)
                                except socket_error as e:
                                    if e.args[0] == 10054: # workaround for this issue: http://support.microsoft.com/kb/263823
                                        continue
                                    else:
                                        raise
                                try:
                                    packet = packet.decode("ascii")
                                except UnicodeDecodeError:
                                    continue
                                self._handle_received_packet(packet, client_addr, client_port)
                            except:
                                pmnc.log.error(exc_string()) # log and ignore

                        # send self-advertisement once in a while

                        if ad_timeout.expired:
                            try:
                                self._purge_known_cages()
                                self._broadcast_advertisement()
                            finally:
                                ad_timeout = self._next_advertisement_timeout()

                    except:
                        pmnc.log.error(exc_string()) # log and ignore

            finally:
                self._bc_socket.close()

        except:
            pmnc.log.error(exc_string()) # log and ignore

###############################################################################

class Handler: # this class is instantiated from interface_tcp

    protocol = "rpc"
    _max_request_size = 1048576
    idle_timeout = 86400.0 # server side of an RPC connection will be kept until
                           # the client closes it, either as idle or expired

    ###################################

    def __init__(self, prev_handler, cage_name):

        self._cage_name = cage_name
        self._rpc_packet = RpcPacket(self._max_request_size)

    ###################################

    @typecheck
    def consume(self, data: bytes) -> bool:

        rpc_request = self._rpc_packet.write(data)
        if rpc_request is not None:
            self._rpc_request = rpc_request
            return True
        else:
            return False

    ###################################

    # this method is executed by one of the interface pool threads and performs
    # the actual processing of a previously read and parsed request

    def process_tcp_request(self):

        rpc_request = self._rpc_request

        # extract call information from the dict

        assert rpc_request["target_cage"] == self._cage_name, "expected call to this cage"

        source_cage = rpc_request["source_cage"]
        module = rpc_request["module"]
        method = rpc_request["method"]
        module_method = "{0:s}.{1:s}".format(module, method)
        args = rpc_request["args"]
        kwargs = rpc_request["kwargs"]

        request_dict = rpc_request["request"]
        request_dict["interface"] = "rpc"
        request_dict["protocol"] = "rpc"

        # auth_tokens are inherited from the RPC interface
        # and updated with the cage name

        original_request = pmnc.request
        auth_tokens = original_request.parameters["auth_tokens"]

        # if the connection arrived over SSL, we verify source
        # cage name against the peer's SSL certificate

        if auth_tokens["encrypted"] and \
           not by_regex("^{0:s}$".format(auth_tokens["peer_cn"]))(source_cage):
            raise Exception("source cage name does not match its SSL certificate")

        auth_tokens.update(source_cage = source_cage)
        request_dict["parameters"]["auth_tokens"] = auth_tokens

        # temporarily impersonate the RPC request, inheriting original request's deadline

        impersonated_request = \
            pmnc.request.from_dict(request_dict, timeout = original_request.remain)

        pmnc.log.info("incoming RPC request {0:s} becomes {1:s} and enters "
                      "{2:s}(), deadline in {3:.01f} second(s)".\
                      format(original_request.unique_id, impersonated_request.unique_id,
                             module_method, impersonated_request.remain))
        try:
            current_thread()._request = impersonated_request
            try:
                result = pmnc.__getattr__(module).__getattr__(method)(*args, **kwargs)
            finally:
                current_thread()._request = original_request # restore the original request
        except:
            error = exc_string()
            pmnc.log.error("incoming RPC request {0:s} has failed in {1:s}(): {2:s}".\
                           format(pmnc.request.unique_id, module_method, error))
            rpc_response = dict(exception = error)
        else:
            pmnc.log.info("incoming RPC request {0:s} has returned from {1:s}()".\
                          format(pmnc.request.unique_id, module_method))
            rpc_response = dict(result = result)

        response_bytes = RpcPacket.marshal(rpc_response)

        self._response = BytesIO()
        self._response.write("{0:08X}{1:s}".\
                             format(len(response_bytes),
                                    sha1(response_bytes).hexdigest().upper()).\
                             encode("ascii") + response_bytes)
        self._response.seek(0, SEEK_SET)

    ###################################

    @typecheck
    def produce(self, n: int) -> bytes:

        return self._response.read(n)

    ###################################

    @typecheck
    def retract(self, n: int):

        self._response.seek(-n, SEEK_CUR)

###############################################################################

class Resource(TransactionalResource): # RPC resource

    @typecheck
    def __init__(self, name, *,
                 broadcast_address: (str, int),
                 discovery_timeout: float,
                 multiple_timeout_allowance: float,
                 flock_id: valid_flock_id,
                 exact_locations: dict_of(valid_cage_name, valid_exact_location),
                 pool__resource_name: valid_cage_name):

        TransactionalResource.__init__(self, name)

        self._cage_name = pool__resource_name
        self._exact_location = exact_locations.get(self._cage_name)

        if self._exact_location is None:
            broadcast_address, self._broadcast_port = broadcast_address
            self._bind_address, self._broadcast_address = broadcast_address.split("/")
            self._discovery_timeout = discovery_timeout
            self._multiple_timeout_allowance = min(multiple_timeout_allowance, 1.0)
            self._flock_id = flock_id
            self._request_prefix = "PYTHOMNIC3K-REQUEST:{0:s}:".format(flock_id)
            self._response_prefix = "PYTHOMNIC3K-RESPONSE:{0:s}:".format(flock_id)
        else:
            self._connect_timeout = discovery_timeout

    ###################################

    def _create_discovery_request(self) -> (bytes, bytes):

        request_id = b2a_hex(urandom(8)).decode("ascii").upper()
        discovery_request = "{0:s}{1:s}:DISCOVER-CAGE:{2:s}".\
                            format(self._request_prefix, request_id, self._cage_name)
        discovery_response_prefix = "{0:s}{1:s}:".format(self._response_prefix, request_id)

        return discovery_request.encode("ascii"), \
               discovery_response_prefix.encode("ascii")

    ###################################

    @typecheck
    def _create_tcp_resource(self, timeout: Timeout, discovered_location: valid_location,
                             remote_addr: optional(str) = None):

        if discovered_location[:6] in ("ssl://", "tcp://") and discovered_location[-1] == "/":
            cage_addr, cage_port = discovered_location[6:-1].split(":")
            if cage_addr == "*":
                assert remote_addr is not None
                cage_addr = remote_addr
        else:
            raise Exception("unsupported RPC protocol")

        if discovered_location.startswith("ssl://"):
            ssl_key_cert_file = _locate_key_file("key_cert.pem")
            ssl_ca_cert_file = _locate_key_file("ca_cert.pem")
        elif discovered_location.startswith("tcp://"):
            ssl_key_cert_file = None
            ssl_ca_cert_file = None

        return pmnc.protocol_tcp.TcpResource(self._cage_name,
                                             server_address = (cage_addr, int(cage_port)),
                                             connect_timeout = timeout.remain,
                                             ssl_key_cert_file = ssl_key_cert_file,
                                             ssl_ca_cert_file = ssl_ca_cert_file)

    ###################################

    def _estimate_node_count(self) -> int:

        rpc_interface = pmnc.interfaces.get_interface("rpc")
        return rpc_interface and len(rpc_interface.get_nodes(self._cage_name)) or 0

    ###################################

    def _discover(self, timeout):

        # during discovery we expect to receive as many responses as
        # there are cage instances currently known through advertising

        expected_responses = self._estimate_node_count()

        pmnc.log.info("discovering cage {0:s}, advertised from {1:d} node(s)".\
                      format(self._cage_name, expected_responses))
        try:

            # if more than one cage is expected to respond, we allow slightly longer
            # initial waiting for responses, controlled by multiple_timeout_allowance

            if expected_responses > 1:
                multiple_timeout_allowance = Timeout(self._multiple_timeout_allowance)

            discovery_request, discovery_response_prefix = self._create_discovery_request()
            received_responses = {}

            # the one-time broadcasting socket must be bound to a random port

            bc_socket = _create_sending_broadcast_socket(self._bind_address)
            try:

                resend_timeout = Timeout(1.0) # broadcast once a second

                while not timeout.expired and not received_responses: # until target cage is discovered or timeout expires

                    # broadcast discovery request

                    bc_socket.sendto(discovery_request, (self._broadcast_address, self._broadcast_port))
                    resend_timeout.reset()

                    # wait for a matching response (there could be more than one)

                    while select([bc_socket], [], [], min(timeout.remain, resend_timeout.remain))[0]:
                        try:

                            packet, (remote_addr, remote_port) = bc_socket.recvfrom(57344)

                            # note that the received packet does not necessarily
                            # contain the discovery response we wait for

                            if remote_port == self._broadcast_port and \
                               packet.startswith(discovery_response_prefix): # but this one is ours

                                # parse the response and append channel instance to the list of discovered

                                discovered_location = packet[len(discovery_response_prefix):].decode("ascii")
                                pmnc.log.debug("received discovery response from {0:s}, cage {1:s} is at {2:s}".\
                                               format(remote_addr, self._cage_name, discovered_location))

                                received_responses[remote_addr] = discovered_location
                                if len(received_responses) >= expected_responses:
                                    break # while select

                            # if some cage instance(s) have already responded, but there are still
                            # more responses to expect, keep waiting within allowance time

                            if received_responses and \
                               (multiple_timeout_allowance.expired or
                                not select([bc_socket], [], [], min(timeout.remain, resend_timeout.remain,
                                                                    multiple_timeout_allowance.remain))[0]):
                                break # while select

                        except:
                            pmnc.log.error(exc_string()) # log and ignore

            finally:
                bc_socket.close()

            # if more than one cage instance has been discovered,
            # pick one at random to improve load balancing

            if received_responses:
                remote_addrs = list(received_responses.keys())
                remote_addr = remote_addrs[randint(0, len(remote_addrs) - 1)]
                discovered_location = received_responses[remote_addr]
                tcp_resource = self._create_tcp_resource(timeout, discovered_location, remote_addr)
            else:
                raise Exception("no discovery response from cage {0:s} in {1:.01f} "
                                "second(s)".format(self._cage_name, timeout.timeout))

        except:
            pmnc.log.error("discovery attempt failed: {0:s}".format(exc_string()))
            raise
        else:
            pmnc.log.info("discovered {0:s}".format(tcp_resource.peer_info))
            return tcp_resource

    ###################################

    def connect(self):

        self._attrs = []

        if self._exact_location is None:
            discovery_timeout = Timeout(min(self._discovery_timeout, pmnc.request.remain))
            self._tcp_resource = self._discover(discovery_timeout)
        else:
            connect_timeout = Timeout(min(self._connect_timeout, pmnc.request.remain))
            self._tcp_resource = self._create_tcp_resource(connect_timeout, self._exact_location)

        self._tcp_resource.connect()

        if self._tcp_resource.encrypted and \
           not by_regex("^{0:s}$".format(self._tcp_resource.peer_cn))(self._cage_name):
            raise Exception("target cage name does not match its SSL certificate")

        TransactionalResource.connect(self)

    ###################################

    def disconnect(self):

        self._tcp_resource.disconnect()
        TransactionalResource.disconnect(self)

    ###################################

    def __getattr__(self, name):

        self._attrs.append(name)
        return self

    ###################################

    def __call__(self, *args, **kwargs):

        attrs, self._attrs = self._attrs, []
        assert len(attrs) == 2, "expected module.method RPC syntax"
        module, method = attrs

        assert not self.resource_args and \
               not self.resource_kwargs, "synchronous remote calls have no options"

        # wrap up an RPC call and assemble a byte stream

        request_dict = pmnc.request.to_dict()

        # remove request parameters that must not cross the RPC border

        del request_dict["interface"]
        del request_dict["protocol"]
        request_parameters = request_dict["parameters"]
        del request_parameters["auth_tokens"]
        request_parameters.pop("retry", None)

        request = dict(source_cage = __cage__,
                       target_cage = self._cage_name,
                       module = module, method = method,
                       args = args, kwargs = kwargs,
                       request = request_dict)

        # convert the request dict into bytes

        request_bytes = RpcPacket.marshal(request)
        request_packet = "{0:08X}{1:s}".\
                         format(len(request_bytes),
                                sha1(request_bytes).hexdigest().upper()).\
                         encode("ascii") + request_bytes

        # send the serialized request, then parse and return the response;
        # note that the marshaled RPC exception is not rethrown here not to
        # cause the disconnect of the resource

        self._response = RpcPacket()
        cage_module_method = "{0:s}.{1:s}.{2:s}()".format(self._cage_name, module, method)

        pmnc.log.info("request {0:s} initiates RPC call {1:s}".\
                      format(pmnc.request.unique_id, cage_module_method))
        try:
            result = self._tcp_resource.send_request(request_packet, self.response_handler)
        except:
            error = exc_string()
            pmnc.log.error("request {0:s} has had its RPC call {1:s} aborted: {2:s}".\
                           format(pmnc.request.unique_id, cage_module_method, error))
            raise
        else:
            pmnc.log.info("request {0:s} has returned with {1:s} from RPC call {2:s}".\
                          format(pmnc.request.unique_id,
                                 "exception" in result and "failure" or "success",
                                 cage_module_method))
            return result

    ###################################

    def response_handler(self, data: bytes) -> optional(dict):

        return self._response.write(data)

###############################################################################

def self_test_loopback(*args, **kwargs):

    if pmnc.request.self_test != __name__:
        raise Exception("invalid access to self-test code")

    return args, kwargs, pmnc.request.to_dict()

###############################################################################

def self_test():

    from pmnc.request import fake_request
    from expected import expected
    from time import sleep

    local_addresses, broadcast_port = \
        pmnc.config_interface_rpc.get("broadcast_address")
    bind_address, broadcast_address = local_addresses.split("/")

    ###################################

    def test_create_broadcast_socket():

        s1 = _create_receiving_broadcast_socket(broadcast_port)
        s2 = _create_receiving_broadcast_socket(broadcast_port)
        s = _create_sending_broadcast_socket(bind_address)

        p = urandom(64)
        s.sendto(p, (broadcast_address, broadcast_port))

        assert select([s1], [], [], 3.0)[0] == [s1]
        packet = s1.recvfrom(57344)[0]
        assert packet == p

        assert select([s2], [], [], 3.0)[0] == [s2]
        packet = s2.recvfrom(57344)[0]
        assert packet == p

    test_create_broadcast_socket()

    ###################################

    def start_interface():

        config = pmnc.config_interface_rpc.copy()
        ifc = pmnc.interface.create("rpc", **config)
        ifc._ad_periods = (1.0, 1.0)
        ifc._cage_name = "somecage"
        ifc.start()
        return ifc

    ###################################

    def test_start_stop_interface():

        ifc = start_interface()
        try:
            assert ifc.listener_address[0] == bind_address
            assert 63000 <= ifc.listener_address[1] < 64000
            assert ifc._broadcast_port == 12481
            Timeout(5.0).wait()
        finally:
            ifc.cease(); ifc.stop()

    test_start_stop_interface()

    ###################################

    def test_create_discovery_request():

        params = pmnc.config_resource_rpc.copy()
        del params["protocol"]           # normally resource.py does this
        del params["pool__idle_timeout"] # normally transaction.py does this
        del params["pool__max_age"]
        r = Resource("test", pool__resource_name = "cage123", **params)

        rq, rsp = r._create_discovery_request()
        rq = rq.decode("ascii"); rsp = rsp.decode("ascii")
        assert by_regex("^PYTHOMNIC3K-REQUEST:SELF_TEST:[0-9A-F]{16}:DISCOVER-CAGE:cage123$")(rq)
        rid = rq.split(":", 4)[2]
        assert rsp == "PYTHOMNIC3K-RESPONSE:SELF_TEST:{0:s}:".format(rid)

    test_create_discovery_request()

    ###################################

    def test_discover_once():

        ifc = start_interface()
        try:

            s = _create_sending_broadcast_socket(bind_address)

            request_id = b2a_hex(urandom(8)).decode("ascii").upper()
            request = "PYTHOMNIC3K-REQUEST:SELF_TEST:{0:s}:DISCOVER-CAGE:{1:s}".\
                      format(request_id, "somecage").encode("ascii")
            response = "PYTHOMNIC3K-RESPONSE:SELF_TEST:{0:s}:ssl://*:{1:d}/".\
                       format(request_id, ifc.listener_address[1]).encode("ascii")

            pmnc.log.debug("sending 3 discovery requests")

            for i in range(3):
                s.sendto(request, (broadcast_address, ifc._broadcast_port))
                sleep(0.5)

            t = Timeout(3.0)
            while not t.expired and select([s], [], [], t.remain)[0]:
                packet = s.recvfrom(57344)[0]
                if packet == response:
                    break
            else:
                raise Exception("no discovery response")

        finally:
            ifc.cease(); ifc.stop()

    test_discover_once()

    ###################################

    def test_advertisement():

        ifc = start_interface()
        try:

            assert not ifc.get_cages()
            assert ifc.get_nodes("somecage") == {}

            timeout = Timeout(5.0)
            while not timeout.expired:
                nodes = ifc.get_nodes("somecage")
                if nodes:
                    assert len(nodes) == 1
                    loc = nodes["self_test"]
                    assert valid_location(loc)
                    assert loc.endswith(":{0:d}/".format(ifc.listener_address[1]))
                    break
                Timeout(1.0).wait()
            else:
                assert False, "should have advertised itself"

        finally:
            ifc.cease(); ifc.stop()

        Timeout(3.0).wait()
        ifc._purge_known_cages()
        assert ifc.get_cages() == {"somecage"}
        assert ifc.get_nodes("somecage") == {}

    test_advertisement()

    ###################################

    def test_exact_location():

        ifc = start_interface()
        try:

            fake_request(pmnc.config_interfaces.get("request_timeout"))

            # wait for the cage to be advertised

            nodes = ifc.get_nodes("somecage")
            while not nodes and not pmnc.request.expired:
                Timeout(1.0).wait()
                nodes = ifc.get_nodes("somecage")
            assert nodes, "should have advertised itself"

            original_request_dict = pmnc.request.to_dict()
            assert original_request_dict.pop("interface") == "-"
            assert original_request_dict.pop("protocol") == "-"
            assert original_request_dict["parameters"].pop("auth_tokens") == {}

            # then initiate connection to now exact known address

            def call_exact_address(module, method, *args, **kwargs):

                resource = pmnc.protocol_rpc.Resource("exact.somecage",
                                                      broadcast_address = ("UNUSED/UNUSED", 0),
                                                      discovery_timeout = 3.0,
                                                      multiple_timeout_allowance = 0.0,
                                                      flock_id = "UNUSED",
                                                      exact_locations = { "somecage": nodes["self_test"] },
                                                      pool__resource_name = "somecage")
                resource.connect()
                try:
                    resource.begin_transaction("xid", source_module_name = __name__,
                                               transaction_options = {}, resource_args = (), resource_kwargs = {})
                    try:
                        result = resource.__getattr__(module).__getattr__(method)(*args, **kwargs)
                    except:
                        resource.rollback()
                        raise
                    else:
                        resource.commit()
                finally:
                    resource.disconnect()

                return result

            # successful call

            result = call_exact_address("protocol_rpc", "self_test_loopback", 1, "2", foo = "bar")

            result = result["result"]
            args, kwargs, request_dict = result
            assert args == (1, "2")
            assert kwargs == { "foo": "bar" }
            assert request_dict.pop("interface") == "rpc"
            assert request_dict.pop("protocol") == "rpc"
            auth_tokens = request_dict["parameters"].pop("auth_tokens")
            del auth_tokens["peer_ip"]
            assert auth_tokens == { "encrypted": True, "peer_cn": ".*", "source_cage": ".shared" }
            original_deadline = original_request_dict.pop("deadline")
            deadline = request_dict.pop("deadline")
            assert abs(original_deadline - deadline) < 0.01
            assert request_dict == original_request_dict

            # exception

            result = call_exact_address("module", "method")

            result = result["exception"]
            assert result.startswith("ModuleNotFoundError(\"file module.py was not found\") ")

        finally:
            ifc.cease(); ifc.stop()

    test_exact_location()

    ###################################

    def test_loopback_request():

        ifc = start_interface()
        try:

            fake_request(pmnc.config_interfaces.get("request_timeout"))

            original_request_dict = pmnc.request.to_dict()
            assert original_request_dict.pop("interface") == "-"
            assert original_request_dict.pop("protocol") == "-"
            assert original_request_dict["parameters"].pop("auth_tokens") == {}

            xa = pmnc.transaction.create()
            xa.rpc__somecage.protocol_rpc.self_test_loopback(1, "2", foo = "bar")
            xa.rpc__somecage.module.method()
            result, exc = xa.execute()

            result = result["result"]
            args, kwargs, request_dict = result
            assert args == (1, "2")
            assert kwargs == { "foo": "bar" }
            assert request_dict.pop("interface") == "rpc"
            assert request_dict.pop("protocol") == "rpc"
            auth_tokens = request_dict["parameters"].pop("auth_tokens")
            del auth_tokens["peer_ip"]
            assert auth_tokens == { "encrypted": True, "peer_cn": ".*", "source_cage": ".shared" }
            original_deadline = original_request_dict.pop("deadline")
            deadline = request_dict.pop("deadline")
            assert abs(original_deadline - deadline) < 0.01
            assert request_dict == original_request_dict

            assert len(exc) == 1
            assert exc["exception"].startswith("ModuleNotFoundError(\"file module.py was not found\") ")

        finally:
            ifc.cease(); ifc.stop()

    test_loopback_request()

    ###################################

    def test_pmnc_syntax():

        ifc = start_interface()
        try:

            fake_request(10.0)

            original_request_dict = pmnc.request.to_dict()
            assert original_request_dict.pop("interface") == "-"
            assert original_request_dict.pop("protocol") == "-"
            assert original_request_dict["parameters"].pop("auth_tokens") == {}

            try:
                pmnc("somecage").foo.bar() # no matter what we call here, the two previously discovered
            except:
                pass
            else:
                assert False

            try:
                pmnc("somecage").biz.baz() # resources are failing and being discarded
            except:
                pass
            else:
                assert False

            with expected(Exception("ModuleNotFoundError(\"file notfound.py was not found\") ")):
                pmnc("somecage").notfound.method()

            pmnc("somecage").protocol_rpc.self_test_loopback() # this should reuse the previous resource

        finally:
            ifc.cease(); ifc.stop()

    test_pmnc_syntax()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF
