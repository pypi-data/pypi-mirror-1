# This module contains configuration for a fake resource, and is only
# used for self-testing of modules transaction.py and shared_pools.py

config = dict \
(
protocol = "test",        # meta
)

# self-tests of shared_pools.py depend on the following configuration

self_test_config = dict \
(
p1 = "v1",
p2 = "v2",
pool__size = 3,           # meta, optional, restricts the maximum pool size
pool__idle_timeout = 1.0, # meta, optional, restricts the resource idle timeout
pool__max_age = 2.0,      # meta, optional, restricts the resource max age
pool__min_time = 0.5,     # meta, optional, restricts the minimum remaining request time to access the resource
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF