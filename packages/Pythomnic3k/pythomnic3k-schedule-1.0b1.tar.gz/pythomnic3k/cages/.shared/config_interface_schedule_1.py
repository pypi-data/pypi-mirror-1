# configuration file for interface "schedule_1"
#
# this file exists as a reference for configuring schedule interfaces
# and to support self-test run of module protocol_schedule.py
#
# copy this file to your own cage, possibly renaming into
# config_interface_YOUR_INTERFACE_NAME.py, then modify the copy

config = dict \
(
protocol = "schedule",     # meta
format = "%H:%M",          # schedule (argument to strftime)
match = "12:30",           # schedule (regular expression to match)
)

# self-tests of protocol_schedule.py depend on the following configuration

self_test_config = dict \
(
format = "%S",
match = "00|03|06|09|12|15|18|21|24|27|30|33|36|39|42|45|48|51|54|57", # every 3 seconds
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF