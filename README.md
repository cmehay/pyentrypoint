# pyentrypoint

__pyentrypoint__ is a tool written in `Python` to manage Docker containers `ENTRYPOINT`.

This tool avoids writing shell scripts to:
 - Handle commands and sub commands
 - Identify linked containers
 - Generate configuration using `jinja2` templates
 - Run commands before starting service
 - Reload service when configuration has changed

[![Documentation Status](https://readthedocs.org/projects/pyentrypoint/badge/?version=latest)](http://pyentrypoint.readthedocs.io/en/latest/?badge=latest) [![Build Status](https://travis-ci.org/cmehay/pyentrypoint.svg?branch=master)](https://travis-ci.org/cmehay/pyentrypoint)


## Changelog

###### v0.7.2 (2020-05-30)
  - add set_environment in settings

###### v0.7.1 (2020-05-24)
  - add envtobool function in configuration template

###### v0.7.0 (2020-05-17)
  - Add command matching setup

###### V0.6.0 (2020-05-10)
  - Drop python 2 support
  - Deprecation of `command` and `subcommands` settings for `commands` (see bellow)

## Usages

### Install in container

All you need to do is to setup a `yaml` file called `entrypoint-config.yml` and to install __pyentrypoint__ in your `Dockerfile` using pip.

```dockerfile
FROM        debian
# Installing git for example
RUN         apt-get update && apt-get install git python-pip -y
# Install pyentrypoint
RUN         pip install pyentrypoint
# Copy config file in the current WORKDIR
COPY        entrypoint-config.yml .
# Set ENTRYPOINT
ENTRYPOINT  ['pyentrypoint']
# git will be the default command
CMD         ['git']
```

```dockerfile
FROM        alpine
# Installing git for example
RUN         apk add --update py-pip git
# Install pyentrypoint
RUN         pip install pyentrypoint
# Copy config file in the current WORKDIR
COPY        entrypoint-config.yml .
# Set ENTRYPOINT
ENTRYPOINT  ['pyentrypoint']
# git will be the default command
CMD         ['git']
```

#### Using docker-image

```dockerfile
FROM    goldy/pyentrypoint:python3

# ONBUILD statement add entrypoint-config.yml in current directories

```

Available with many flavours:

- `goldy/pyentrypoint:python3`
- `goldy/pyentrypoint:python3.6`
- `goldy/pyentrypoint:python3.7`
- `goldy/pyentrypoint:python3.8`
- `goldy/pyentrypoint:python3-alpine`
- `goldy/pyentrypoint:python3.6-alpine`
- `goldy/pyentrypoint:python3.7-alpine`
- `goldy/pyentrypoint:python3.8-alpine`




### Working examples
 - [Tor hidden service](https://github.com/cmehay/docker-tor-hidden-service)

### Setup entrypoint

This is an example of `entrypoint-config.yml` file.

```yaml
# Entrypoint configuration example

# This setup lists commands handled by entrypoint.
# If you run the container with a command not in this list,
# pyentrypoint will run the command directly without any action
# If this setting and `command` are not set, all commands will be handled.
# Support wildcard
commands:
    - git
    - sl*

# DEPRECATED: This setup is remplaced by `commands`
# This entry should reflect CMD in Dockerfile
# If `commands` is present, this setup will be ignored.
# DEPRECATED: This setup is remplaced by `commands`
command: git

# DEPRECATED: This setup will be dropped
# This is a list with some subcommands to handle
# when CMD is not `git` here.
# By default, all args started with hyphen are handled.
# DEPRECATED: This setup will be dropped
subcommands:
    - "-*"
    - clone
    - init
    - ls-files
    # etc...

# User and group to run the cmd.
# Can be name or uid/gid.
# Affect only command handled.
# Dockerfile USER value by default.
user: 1000
group: 1000

# These files should exist (ADD, COPY or mounted)
# and should be jinja templated.
# Note: if config files end with ".tpl", the extension will be removed.
config_files:
    - /etc/gitconfig
    - .ssh/config.tpl # Will apply to ".ssh/config"
    - /tmp/id_rsa: .ssh/id_rsa # Will apply "/tmp/id_rsa" template to ".ssh/id_rsa"


# These environment variables will be wiped before
# exec command to keep them secret
# CAUTION: if the container is linked to another one,
# theses variables will passed to it anyway
secret_env:
    - SSHKEY
    - '*' # Support globbing, all environment will be wiped

# Links are handled here
# Port, name, protocol or env variable can be used to identify the links
# Raise an error if the link could not be identified
# This is not supported when using docker network or docker-compose v2.
links:
    'ssh':
        port: 22
        name: 'ssh*'
        protocol: tcp
        # env can be list, dictionary or string
        env:
            FOO: bar
        # Single doesn't allow multiple links for this ID
        # false by default
        single: true
        # Set to false to get optional link
        # true by default
        required: true

# Set custom environment variable by running commands
# Will run before pre_conf_commands and capture stdout only
# Stop init if crash
set_environment:
    - ENV_1: echo 'The environment variable ENV_1 will be added with this phrase'
    - ENV_2: head /dev/urandom | base64
    - ENV_3: echo ${ENV_1} and ${ENV_2} are now available here
    - ENV_4: exit 1 || true  # Set like this if you need to ignore error

# Commands to run before applying configuration
pre_conf_commands:
    - echo something > to_this_file

# commands to run after applying configuration
post_conf_commands:
    - echo "something else" > to_this_another_file

# commands to run in parallele with the main command
post_run_commands:
    - echo do something in parallele with the main command

# run post_run_commands in parallele or sequentially (default is sequential)
run_post_commands_in_parallele: true # default false

# Reload service when configuration change by sending a signal to process
reload:
    signal: SIGHUP # Optional, signal to send, default is SIGHUP
    pid: 1 # Optional, pid to send signal, default is 1
    watch_config_files: true # Optional, watch defined config files, default True
    files: # Optional, list of files to watch
        - /etc/conf/to/watch
        - /file/support/*.matching
# can also be enabled like this:
reload: true


# Cleanup environment from variables created by linked containers
# before running command (True by default)
clean_env: true

# Enable debug to debug
debug: true

# Do not output anything except error
quiet: false
```

#### Handled command matching

All settings can be mapped to an handled command.

For instance:

```yaml

# This config will handle command `abc` and `xyz`
commands:
  - abc
  - xyz

# you can map commands to handled commands bellow
pre_conf_commands:
  - abc:
    - echo "will run for command abc"
  - xyz:
    - echo "will run for command xyz"
    - echo "Can be multiple"
  - echo "Will run for both commands"

user:
  - abc: 1000
  - xyz: 1001

# Mapping can also be a dictionnary
group:
  abc: 1000
  xyz: 1001

# Etc
```

Not supported for deprecated settings `command`, `subcommands` and `links`.



### Config templates

You can generate configuration for your service with jinja2 template.

**`links` and `containers` are not supported with docker network and docker-compose v2.**

Here is an example for an hypothetical ssh config file:

```jinja
host server:
    hostname {{links.ssh.ip}}
    port {{links.ssh.port}}
```

Templates will be replaced with ip address and port of the identified link. All links can be accessed from `links.all`, this is a tuple of links you can iterate on it.

```jinja
{% for link in links.all %}
host {{link.names[0]}}
    hostname {{link.ip}}
    port {{links.port}}
{% endfor %}
```

If you change the option `single` to `false` in the `entrypoint-config.yml`, the identified link `ssh` will become a tuple of links. You must iterate on it in the `jinja` template.

```jinja
{% for link in links.ssh %}
host {{link.names[0]}}
    hostname {{link.ip}}
    port {{links.port}}
{% endfor %}
```

Accessing environment in template.

```jinja
{% if 'SSHKEY in env' %}
{{env['SSHKEY']}}
{% endfor %}
```

### Accessible objects

You have 4 available objects in your templates.

 - `config`
 - `links`
 - `containers`
 - `environ`
 - `yaml`
 - `json`

#### config

`Config` reflect the config file. You can retrieve any setup in this object.

(see `config.py`)

#### links

**Not supported with docker network and docker-compose v2**

`Links` handles `Link` objects. You can identify links using wildcard patterns in the configuration file.

`link` is related to one physical link (one ip and one port).

`link` handles the following attributes:
  - `ip`
    - link ip
  - `port`
    - link port (integer)
  - `environ`
    - related container environment
  - `protocol`
    - link protocol (`tcp` or `udp`)
  - `uri`
    - link URI (example: `tcp://10.0.0.3:80`)
  - `names`
    - tuple of related container names

#### containers

**Not supported with docker network and docker-compose v2**

`containers` handles a tuple of `container` object.

`container` handles the following attributes:
  - `ip`
    - container ip
  - `environ`
    - container environment
  - `names`
    - List of containers names
      - Names are sorted by length, but container ID will be the last element.
  - `id`
    - Hexadecimal container ID (if available, empty string else)
  - `links`
    - Tuple of `link` objects related to this container

#### environ
`environ` is the environment of the container (os.environ).

`env` is an alias to `environ`.

##### envtobool
`envtobool` function is a useful to parse boolean string input in environnement to enable or disable features.

The function accepts a default value as second parameter.

```jinja
{% if envtobool('SOME_ENV_VARIABLE', False) %}
do stuff
{% endif %}

# Will write True or False here
{envtobool('SOME_OTHER_ENV_VARIABLE', True)}
```

See https://docs.python.org/3/distutils/apiref.html#distutils.util.strtobool for information on input.

#### yaml and json

`yaml` and `json` objects are respectively an import of [`PyYAML`](http://pyyaml.org/) and [`json`](https://docs.python.org/2/library/json.html) modules.

They are useful to load and dump serialized data from environment.

```jinja
# Here yaml is present in SETUP_YAML environment variable
{% set data = yaml.load(env['SETUP_YAML'])%}
{{data['param']}}

# Here json is present in SETUP_JSON environment variable
{% set data = json.loads(env['SETUP_JSON'])%}
{{data['param']}}
```

## Setup

Some setups can be overridden using environment variables.

- `ENTRYPOINT_CONFIG` overrides path of `entrypoint-config.yml` file.
- `ENTRYPOINT_FORCE` is applying configuration and runs pre and post conf commands even if the `command` provided is not handled.
- `ENTRYPOINT_PRECONF_COMMAND` run an extra pre conf shell command after all pre conf commands.
- `ENTRYPOINT_POSTCONF_COMMAND` run an extra post conf shell command after all post conf commands.
- `ENTRYPOINT_DEBUG` enables debug logs.
- `ENTRYPOINT_RAW` does not use logging to display pre and post conf commands.
   This can be useful if output is serialized.
- `ENTRYPOINT_DISABLE_RELOAD` disable reload system even if it is enabled in `entrypoint-config.yml`.
- `ENTRYPOINT_USER` overrides `user` in config.
- `ENTRYPOINT_GROUP` overrides `group` in config.
- `ENTRYPOINT_DISABLE_SERVICE` exits container with 0 before doing anything. Useful to disable container using environement.



### Running Tests

To run tests, ensure that `docker-compose` and `make` are installed and run

```shell
$ make test
```
