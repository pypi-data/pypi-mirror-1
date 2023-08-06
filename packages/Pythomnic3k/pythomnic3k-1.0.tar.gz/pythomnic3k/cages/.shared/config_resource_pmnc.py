# configuration file for resource "pmnc"
#
# there is really just one resource of protocol "pmnc" per cage,
# no need to ever configure another or to change this one, therefore
# this file is pretty much static and need not to be copied to
# each cage
#
# note that the resource is called pmnc, but the implementation is
# delegated to protocol "retry", the reason for this is that pmnc
# looks better in
#
# xa = pmnc.transaction.create()
# xa.pmnc("somecage:retry").module.method()
# call_id = xa.execute()[0]

config = dict \
(
protocol = "retry", # meta, nothing to configure here
)

self_test_config = dict \
(
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF