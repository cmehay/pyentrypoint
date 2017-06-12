Templates
=========

You can generate configuration for your service with jinga2 template.

Here is an example for an hypothetical ssh config file:

.. code:: jinja

    host server:
        hostname {{links.ssh.ip}}
        port {{links.ssh.port}}

Templates will be replaced with ip address and port of the identified
link. All links can be accessed from ``links.all``, this is a tuple of
links you can iterate on it.

.. code:: jinja

    {% for link in links.all %}
    host {{link.names[0]}}
        hostname {{link.ip}}
        port {{links.port}}
    {% endfor %}

If you change the option ``single`` to ``false`` in the
``entrypoint-config.yml``, the identified link ``ssh`` will become a
tuple of links. You must iterate on it in the ``jinja`` template.

.. code:: jinja

    {% for link in links.ssh %}
    host {{link.names[0]}}
        hostname {{link.ip}}
        port {{links.port}}
    {% endfor %}

Accessing environment in template.

.. code:: jinja

    {% if 'SSHKEY in env' %}
    {{env['SSHKEY']}}
    {% endfor %}

Accessible objects
~~~~~~~~~~~~~~~~~~

You have 4 available objects in your templates.

-  ``config``
-  ``links``
-  ``containers``
-  ``environ``

``links`` and ``containers`` are not supported by docker network or docker-compose v2.

config
^^^^^^

``Config`` reflect the config file. You can retrieve any setup in this
object.

(see ``config.py``)

links
^^^^^

**Not supported when using docker network or docker-compose v2.**

``Links`` handles ``Link`` objects. You can identify links using
wildcard patterns in the configuration file.

``link`` is related to one physical link (one ip and one port).

``link`` handles the following attributes: - ``ip`` - link ip - ``port``
- link port (integer) - ``environ`` - related container environment -
``protocol`` - link protocol (``tcp`` or ``udp``) - ``uri`` - link URI
(example: ``tcp://10.0.0.3:80``) - ``names`` - tuple of related
container names

containers
^^^^^^^^^^

**Not supported when using docker network or docker-compose v2.**

``containers`` handles a tuple of ``container`` object.

``container`` handles the following attributes: - ``ip`` - container ip
- ``environ`` - container environment - ``names`` - List of containers
names - Names are sorted by length, but container ID will be the last
element. - ``id`` - Hexadecimal container ID (if available, empty string
else) - ``links`` - Tuple of ``link`` objects related to this container

environ
^^^^^^^

``environ`` is the environment of the container (os.environ).

``env`` is an alias to ``environ``.

``yaml`` and ``json``
^^^^^^^^^^^^^^^^^^^^^

``yaml`` and ``json`` objects are respectively an import of `PyYAML <http://pyyaml.org/>` and `json <https://docs.python.org/2/library/json.html> modules.

They are useful to load and dump serialized data from environment.

.. code:: jinja
    # Here yaml is present in SETUP_YAML environment variable
    {% set data = yaml.load(env['SETUP_YAML'])%}
    {{data['param']}}

    # Here json is present in SETUP_JSON environment variable
    {% set data = json.loads(env['SETUP_JSON'])%}
    {{data['param']}}
