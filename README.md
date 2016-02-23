# pyentrypoint

__pyentrypoint__ is a tool written in `Python` to manager Docker containers `ENTRYPOINT`.

This tool avoids writing shell scripts to:
 - Handle commands and sub commands
 - Identify linked containers
 - Generate configuration using `jinja2` templates
 - Run commands before starting service


## Usages

### Install in container

All you need to do is to setup a `yaml` file called `entrypoint-config.yml` and to install __pyentrypoint__ in your `Dockerfile` using pip.

```dockerfile
FROM        debian
# Installing git for example
RUN         apt-get update && apt-get install git -y
# Install pyentrypoint
RUN         pip install pyentrypoint
# Copy config file in the current WORKDIR
COPY        entrypoint-config.yml .
# Set ENTRYPOINT
ENTRYPOINT  ['pyentrypoint']
# git will be the default command
CMD         ['git']
```

### Setup entrypoint

This is an example of `entrypoint-config.yml` file.

```yaml
# Entrypoint configuration example

# This entry should reflect CMD in Dockerfile
command: git

# This is a list with some subcommands to handle
# when CMD is not `git` here.
# By default, all args started with hyphen are handled.
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

# These files should exist (ADD or COPY)
# and should be jinja templated.
config_files:
    - /etc/gitconfig
    - .ssh/config
    - .ssh/id_rsa

# These environment variables will be wiped before
# exec command to keep them secret
# CAUTION: if the container is linked to another one,
# theses variables will passed to it anyway
secret_env:
    - SSHKEY

# Links are handled here
# Port, name, protocol or env variable can be used to identify the links
# Raise an error if the link could not be identified
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

# Commands to run before applying configuration
pre_conf_commands:
    - echo something > to_this_file

# commands to run after applying configuration
post_conf_commands:
    - echo "something else" > to_this_another_file

# Cleanup environment from variables created by linked containers
# before running command (True by default)
clean_env: True

# Enable debug to debug
debug: true
```

### Config templates

You can generate configuration for your service with jinga2 template.

Here an example for an hypothetical ssh config file:

```jinga
host server:
    hostname {{links.ssh.ip}}
    port {{links.ssh.port}}
```

Templates with be replaced with ip address and port of the identified link. All links can be accessed from `links.all`, this is a tuple of links you can iterate on it.

```jinga
{% for link in links.all %}
host {{link.names[0]}}
    hostname {{link.ip}}
    port {{links.port}}
{% endfor %}
```

If you change the option `single` to `false` in the `entrypoint-config.yml`, the identified link `ssh` will become a tuple of links. You must iterate on it in the `jinja` template.

```jinga
{% for link in links.ssh %}
host {{link.names[0]}}
    hostname {{link.ip}}
    port {{links.port}}
{% endfor %}
```

### Accessible object

You have 4 available objects in your templates.

 - `config`
 - `links`
 - `containers`
 - `environ`

#### config

`Config` reflect the config file. You can retrieve any setup in this object.

(see `config.py`)

#### links

`Links` handles `Link` objects. You can identify links using globing patterns in the configuration file.

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
    - link uri (example: `tcp://10.0.0.3:80`)
  - `names`
    - tuple of related container names

#### containers
`containers` handles a tuple of `container` object.

`container` handles the following attributes:
  - `ip`
    - container ip
  - `environ`
    - container environment
  - `names`
    - List of containers names
  - `links`
    - Tuple of `link` object related to this container

#### environ
`environ` is the environment of the container (os.environ).

### Running Tests

To run tests, ensure that `docker-compose` and `make` are installed and run

```shell
$ make test
```
