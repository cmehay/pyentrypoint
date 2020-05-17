pyentrypoint-config.yml
=======================

This is an example of ``entrypoint-config.yml`` file.

.. code:: yaml

    # Entrypoint configuration example

    # This entry list commands handled by entrypoint.
    # If you run the container with a command not in this list,
    # pyentrypoint will run the command directly without any action
    # If this option and `command` are not set, all commands will be handled.
    # Support wildcard
    commands:
        - git
        - sl*

    # DEPRECATED: This option is remplaced by `commands`
    # This entry should reflect CMD in Dockerfile
    # If `commands` is present, this option will be ignored.
    # DEPRECATED: This option is remplaced by `commands`
    command: git

    # DEPRECATED: This option will be dropped
    # This is a list with some subcommands to handle
    # when CMD is not `git` here.
    # By default, all args started with hyphen are handled.
    # DEPRECATED: This option will be dropped
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
            # env can be list, dict or string
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

    post_run_commands:
        - echo run commands after started service

    # Reload service when configuration change by sending a signal to process
    reload:
        signal: SIGHUP # Optional, signal to send, default is SIGHUP
        watch_config_files: true # Optional, watch defined config files, default True
        files: # Optional, list of files to watch
            - /etc/conf/to/watch
    # can also be enabled with a boolean:
    reload: true

    # Cleanup environment from variables created by linked containers
    # before running command (True by default)
    clean_env: true

    # Enable debug to debug
    debug: true

    # Do not output anything except error
    quiet: false


yaml references
~~~~~~~~~~~~~~~

commands
^^^^^^^^
This setup lists commands handled by entrypoint.
If you run the container with a command not in this list,
pyentrypoint will run the command directly without any action
If this setting and `command` are not set, all commands will be handled.
Support wildcard

.. code:: yaml
commands:
    - git
    - sl*

command
^^^^^^^

``command`` should reflect CMD in Dockerfile.

If the container is not started with this commande,
the configuration will not be applied.

.. pull-quote::

    **DEPRECATED**: This setup is remplaced by ``commands``.

subcommands
^^^^^^^^^^^

``subcommands`` is a list with some subcommands to handle.

Running container with a matching subcommand run it with setuped ``command``.

.. code:: yaml

    subcommands:
        - "-*"
        - clone
        - init
        - ls-files

.. pull-quote::

    **DEPRECATED**: This setup will be dropped.

    By default, all args started with hyphen are handled.

user, group
^^^^^^^^^^^

User and group to run the ``command``.
Can be name or uid/gid.
Affect only command handled.

.. code:: yaml

    user: 1000
    group: root

.. pull-quote::

    **Note**: Dockerfile USER value by default.

Can be expended from environment in ``ENTRYPOINT_USER`` and ``ENTRYPOINT_GROUP``.

config_files
^^^^^^^^^^^^

These files should exist (ADD or COPY) and should be jinja templated.

.. code:: yaml

    config_files:
        - /etc/gitconfig
        - .ssh/config.tpl # Will apply to ".ssh/config"
        - /tmp/id_rsa: .ssh/id_rsa # Will apply "/tmp/id_rsa" template to ".ssh/id_rsa"

.. pull-quote::
    **Note**: if config files end with ".tpl", the extension will be removed.

secret_env
^^^^^^^^^^

These environment variables will be wiped before
running command to keep them secret.

.. code:: yaml

    secret_env:
        - SSHKEY
        - APIKEY

.. pull-quote::

    **CAUTION**: if the container is linked to another one,
    theses variables will be sent to it anyway.


links
^^^^^

**Not supported when using docker network or docker-compose v2.**

Links are handled here.

Port, name, protocol or environment variables can be used to identify the links.

.. code:: yaml

    links:
        'ssh': # This is the name to handle link in templates
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

.. pull-quote::

    **Note**: All parameters are optionals.

    Raise an error if the link could not be identified.


pre_conf_commands
^^^^^^^^^^^^^^^^^

List of shell commands to run before applying configuration

.. code:: yaml

    pre_conf_commands:
        - echo something > to_this_file


post_conf_commands
^^^^^^^^^^^^^^^^^^

List of shell commands to run after applying configuration

.. code:: yaml

    post_conf_commands:
        - echo "something else" > to_this_another_file

post_run_commands
^^^^^^^^^^^^^^^^^^

List of shell commands to run after service is started

.. code:: yaml

    post_run_commands:
        - sleep 5
        - echo "something else" > to_this_another_file


reload
^^^^^^

Send SIGHUP to PID 1 to reload service when configuration change

Accept boolean or dictionary

.. code:: yaml

    reload:
        signal: SIGHUP # Optional, signal to send, default is SIGHUP
        watch_config_files: true # Optional, watch defined config files, default True
        files: # Optional, list of files to watch
            - /etc/conf/to/watch
            - /file/support/*.matching
    # can also be enabled with a boolean:
    reload: true

clean_env
^^^^^^^^^

Cleanup environment from variables created by linked containers
before running command (True by default)

debug
^^^^^

Print some debug.

quiet
^^^^^

Do not output anything except error


Handled command matching
========================

All settings can be mapped to an handled command.

For instance:

.. code:: yaml

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

Not supported for deprecated settings `command`, `subcommands` and `links`.
