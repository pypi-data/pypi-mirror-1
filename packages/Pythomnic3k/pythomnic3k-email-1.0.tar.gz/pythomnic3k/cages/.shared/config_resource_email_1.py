# configuration file for resource "email_1"
#
# this file exists as a reference for configuring email resources
# and to support self-test run of module protocol_email.py
#
# copy this file to your own cage, possibly renaming into
# config_resource_YOUR_RESOURCE_NAME.py, then modify the copy

config = dict \
(
protocol = "email",                           # meta
server_address = ("mail.domain.com", 25),     # tcp
connect_timeout = 3.0,                        # tcp
encoding = "windows-1251",                    # email
helo = "hostname",                            # email
username = None,                              # email, optional
password = None,                              # email, optional
)

# self-tests of protocol_email.py depend on the following configuration

self_test_config = dict \
(
server_address = ("mail.domain.com", 25),
encoding = "windows-1251",
helo = "hostname",
username = "test2",
password = "pass2",
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF