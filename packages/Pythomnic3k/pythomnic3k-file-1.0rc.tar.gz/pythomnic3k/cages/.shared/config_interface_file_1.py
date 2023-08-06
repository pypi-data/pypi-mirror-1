# configuration file for interface "file_1"
#
# this file exists as a reference for configuring file interfaces
# and to support self-test run of module protocol_file.py
#
# copy this file to your own cage, possibly renaming into
# config_interface_YOUR_INTERFACE_NAME.py, then modify the copy

config = dict \
(
protocol = "file",                       # meta
source_directory = "/tmp",               # file
filename_regex = "[A-Za-z0-9_]+\\.msg",  # file
interval = 10.0,                         # file
)

# self-tests of protocol_file.py depend on the following configuration

self_test_config = dict \
(
source_directory = "/tmp",
interval = 2.0,
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF