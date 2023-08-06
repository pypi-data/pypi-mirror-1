# this file contains various configuration parameters for the module
# state.py, there is hardly any reason for changing anything here

config = dict \
(
checkpoint_interval = 90.0, # seconds between state checkpoints
)

# self-tests of state.py depend on the following configuration

self_test_config = dict \
(
checkpoint_interval = 3.0,
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF