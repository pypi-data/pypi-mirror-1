# configuration file for interface "jms_1"
#
# this file exists as a reference for configuring JMS interfaces
# and to support self-test run of module protocol_jms.py
#
# copy this file to your own cage, possibly renaming into
# config_interface_YOUR_INTERFACE_NAME.py, then modify the copy

config = dict \
(
protocol = "jms",                                                  # meta
java = "C:\\JDK\\BIN\\java.exe",                                   # jms
arguments = ("-Dfile.encoding=windows-1251", ),                    # jms
classpath = "c:\\pythomnic3k\\lib;c:\\pythomnic3k\\lib\\jms.jar;"  # jms
            "c:\\pythomnic3k\\lib\\imq.jar;c:\\pythomnic3k\\lib\\fscontext.jar",
jndi = { "java.naming.factory.initial": "com.sun.jndi.fscontext.RefFSContextFactory",
         "java.naming.provider.url": "file:///c:/pythomnic3k/lib/jndi" }, # jms
factory = "connection_factory",                                    # jms
queue = "work.queue",                                              # jms
username = "user",                                                 # jms
password = "pass",                                                 # jms
)

# self-tests of protocol_jms.py depend on the following configuration

self_test_config = dict \
(
queue = "test.queue",
)

# DO NOT TOUCH BELOW THIS LINE

__all__ = [ "get", "copy" ]

get = lambda key, default = None: pmnc.config.get_(config, self_test_config, key, default)
copy = lambda: pmnc.config.copy_(config, self_test_config)

# EOF