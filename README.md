# Configuration Generation
This tool is used to populate configuration templates and offers a keystore to
hold reusable values. This key store also supports a profile that you can use
to separate your production values from your development values. Or, however
you find it usefull.

# KeyStore
You will need to setup a keystore that holds your configuration values. You can
generate a configuration file simply by running config-gen add-store. See -h
for more information.

Currently all key store data is stored in clear text ini files but the system
will be extended to use encryption at some point. Pull requests welcome!

# Command Line tools
This package installs 2 command line tools:
- config-gen: A utility for management your keystores and profiles.
- cfgen: A short cut to render template files.
