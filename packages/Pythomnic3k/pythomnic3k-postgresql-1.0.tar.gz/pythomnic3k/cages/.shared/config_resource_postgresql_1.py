# configuration file for resource "postgresql_1"
#
# this file exists as a reference for configuring postgresql resources
# and to support self-test run of module protocol_postgresql.py
#
# copy this file to your own cage, possibly renaming into
# config_resource_YOUR_RESOURCE_NAME.py, then modify the copy

config = dict \
(
protocol = "postgresql_pg8000",             # meta
decimal_precision = (10, 2),                # sql
server_address = ("db.domain.com", 5432),   # postgresql
connect_timeout = 3.0,                      # postgresql
database = "database",                      # postgresql
username = "user",                          # postgresql
password = "pass",                          # postgresql
)

# self-tests of protocol_postgresql.py depend on the following configuration

self_test_config = dict \
(
server_address = ("test.postgres", 8304),
database = "test_db",
username = "user",
password = "pass",
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF