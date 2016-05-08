Options setup
=============

Some setups can be overridden using environment variables in the container.

-  ``ENTRYPOINT_CONFIG`` overrides path of ``entrypoint-config.yml``
   file.
-  ``ENTRYPOINT_FORCE`` applies configuration and runs pre and post conf
   commands even if the ``command`` provided is not handled.
- ``ENTRYPOINT_DEBUG`` enables debug logs.
- ``ENTRYPOINT_RAW`` does not use logging to display pre and post conf commands.
   This can be useful if output is serialized.
