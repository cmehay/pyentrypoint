Installation
============

All you need to do is to setup a ``yaml`` file called
``entrypoint-config.yml`` and to install **pyentrypoint** in your
``Dockerfile`` using pip.

.. code:: dockerfile

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

.. code:: dockerfile

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
