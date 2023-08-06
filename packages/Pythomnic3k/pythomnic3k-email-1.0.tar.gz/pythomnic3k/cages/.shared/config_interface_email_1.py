# configuration file for interface "email_1"
#
# this file exists as a reference for configuring e-mail interfaces
# and to support self-test run of module protocol_email.py
#
# copy this file to your own cage, possibly renaming into
# config_interface_YOUR_INTERFACE_NAME.py, then modify the copy

config = dict \
(
protocol = "email",                         # meta
server_address = ("mail.domain.com", 110),  # tcp
connect_timeout = 3.0,                      # tcp
interval = 600.0,                           # email
username = "user",                          # email
password = "pass",                          # email
)

# self-tests of protocol_email.py depend on the following configuration

self_test_config = dict \
(
server_address = ("mail.domain.com", 110),
interval = 5.0,
username = "test1",
password = "pass1",
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF