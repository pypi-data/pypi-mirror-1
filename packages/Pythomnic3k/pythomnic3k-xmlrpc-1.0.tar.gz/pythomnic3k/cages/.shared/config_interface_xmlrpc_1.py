# configuration file for interface "xmlrpc_1"
#
# this file exists as a reference for configuring XMLRPC interfaces
# and to support self-test run of module protocol_xmlrpc.py
#
# copy this file to your own cage, possibly renaming into
# config_interface_YOUR_INTERFACE_NAME.py, then modify the copy

config = dict \
(
protocol = "xmlrpc",                      # meta
listener_address = ("0.0.0.0", 80),       # tcp
max_connections = 100,                    # tcp
ssl_key_cert_file = None,                 # ssl
ssl_ca_cert_file = None,                  # ssl
response_encoding = "windows-1251",       # http
original_ip_header_fields = (),           # http
keep_alive_support = True,                # http
keep_alive_idle_timeout = 120.0,          # http
keep_alive_max_requests = 10,             # http
)

# self-tests of protocol_xmlrpc.py depend on the following configuration

self_test_config = dict \
(
listener_address = ("127.0.0.1", 23673),
max_connections = 100,
ssl_key_cert_file = None,
ssl_ca_cert_file = None,
response_encoding = "windows-1251",
original_ip_header_fields = ("X-Forwarded-For", ),
keep_alive_support = True,
keep_alive_idle_timeout = 3.0,
keep_alive_max_requests = 3,
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF