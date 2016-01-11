# Overview
config-gen is a tool that simplifies management of application configuration
files. It offers a command line interface that can be used to get started
quickly as well as a set of classes that can be used for automation with your
CIS or deployment tools.

Currently, only INI based keystores are supported but the system offers a
adapter model that can be used to write your own keystore adapter with redis,
consol or any storage engine you would like.

# Getting Started
To get started using config-gen, there are a few things you need to do. Please
keep in mind that there are many ways to use this tool and here we only provide
a basic use-case.

- Clone the project and install the package.

```bash
# Install config-gen
python2 setup.py install
```

- Initialize the default library. Note, use -h to see other options for init.

```bash
# Initialize library
config-gen-init
```

- Setup your default keystore.
You will need to add keys to your keystore. Items such as database passwords or
log levels that make sense for your environment.

```bash
# Example keys
config-gen-keys add PYTHON_LOGLEVEL DEBUG
config-gen-keys add APPLICATION_DATABASE_URI mysql://user:password@host/app
```

- Create your application configuration template.
The configuration template would be located in the application directory that
uses the configuration file. The template has a specific format but can be used
with any structure assuming the requirements below are met.

First, the config.template must have the target path on the first line of the
file.

Second, the render processor uses the jinja2 template engine so keys must be
referenced according to jinja 2 syntax: {{ KEY }}.

Example config.template:
```ini
./config.ini
[some-section]
app_db: {{ APPLICATION_DATABASE_URI }}
log_level: {{ PYTHON_LOGLEVEL }}
```

_NOTE: Since jinja2 is used, any jinja2 directives can be used including loops,
branching and raw directives. See jinja2 documentation for details._

- You are ready to render your template.
Make sure your current working directory contains your config.template that you
want to render. See -h for more options.

```bash
config-gen
```


# Command Line Interface
config-gen offerse a set of command line tools for developers and devops teams
to get started quickly. With these tools you can manage libraries, keystores,
and render configuration files for your application and services.

## config-gen-init
This tool is used to initialize a library. It will create the library and add
the library specific default keystore.  You can have as many libraries as you
like but if you use a custom location for a library, you will need to specify
the path using the -l argument to the other command line tools. See -h for all
of the options.

__WARNING: config-gen-init initializes a NEW library. If the specified target
already exists, the existing refrences will be clobbered.__

## config-gen-store
This tool is used to manage keystores within a library. You can create
keystores for each of your environments or each of your applications or both.
It all depends on how you want to use it.

The keystore name is used to uniquely identify the keystore within the current
library. A name might be something like PROD, DEV, or SIT. Or you could create
stores for each application/service. You can even mix the 2 ideas with a
namespace separator such as MY_APP:DEV, MY_APP:PROD. It is really up to you and
the only limitation is that no spaces and some special characters cannot be
used. (Character limitations depend on the keystore type).

The keystore type tells the system what format the keystore is in. Currently
only INI and redis types are supported but can be extended by adding your own
adapters to define the basic operations to get, set and delete values.

The keystore uri tells the type adapter how to connect to the keystore. See the
documentation on the specific keystore type adapter for more information.

See -h for all the options.

## config-gen-key
This tool is used to manage the keys and values inside a specific keystore.
It's pretty basic: Use -h to see all the options.


## config-gen
This is the tool used to render templates. By default, it looks for
config.template in the current working directory but can be changed using
parameters. See -h for all the options.

_Note: The file name - is STDOUT or STDIN depending if the stream is used for
reading or writing. This is handy if you want to render a template to the
screen instead of a file._

## Global Options
There are a few global options that effect 2 or more of the command line tools.

### Verbosity
The -v command can be used on any of the tools and tell the system to print
more details about what it is doing. The underline system uses the python
logger and the number of v's specifies the loglevel.

- 1 'v' means, only show critical messages.
- 2 'v's mean, show critical and error messages.
- 3 'v's mean, show critical, error, and warning messages.
- 4 'v's mean, show critical, error, warning, and info messages.
- 5 'v's mean, show critical, error, warning, info, and debug messages.

### Library
The -l, --library argument can be used to tell the config-gen system to use a
specific library located at the provided path. In the case of config-gen-init
this path is used to tell the system where to initialize a new library.

### Store
The -s, --store argument is available on both config-gen-keys and config-gen
commands. It tells the system what keystore to use. For example, if you wanted
to render a template using your DEVEL keystore, you would issue this command:

```bash
config-gen -s DEVEL
```

# Adapters
The adapter is responsible for marshaling data between config-gen and the
underline storage engine where the values will persist. Currently, there are
two adapters, redis and ini. But the interface is simple if you wanted to build
your own or extend an existing one.

## INI Adapter
The INI adapter is a basic keystore using the local file system. It follows the
standard INI format and can be used for local key storage for multiple
environments or applications. 

The URI for the ini adapter can specify the path and section to use. Here is
the structure: 

```
file://<PATH>?<SECTION>
```

The ini file can already exist when you add it to a library, provided it is in
the correct format. Also, Each section is used as one keystore. This allows you
to store multiple keystores in one ini file.

Example:
```ini
[_DEFAULT]
some_key=Some value

[DEVEL]
some_key=Some other vaule
```

_Note: If no section is provided, a default name will be used. This is not the
ini default section but a config-gen default section. They are different,
remember that._

## Redis Adapter
The Redis adapter is a keystore using a redis server. It is very flexable and
allows you to share keystore values with multiple people that have access to
that server.

The URI for the redis adapter can specify the password, hostname, port, db
index and keystore to use. Here is the structure:

```
redis://:<PASSWORD>@<HOSTNAME>:<PORT>/<DB_INDEX>?<KEYSTORE>
```

The fields password, port, and db_index are optional.

The redis keystore can already exist when you add it to a library, provided it
is in the correct format. Also, keys are stored in a redis hashmap under the
key keystore:___KEYSTORE___
