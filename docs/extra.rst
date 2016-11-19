Options setup
=============

Some setups can be overridden using environment variables in the container.

-  ``ENTRYPOINT_CONFIG`` overrides path of ``entrypoint-config.yml``
   file.
-  ``ENTRYPOINT_FORCE`` applies configuration and runs pre and post conf
   commands even if the ``command`` provided is not handled.
-  ``ENTRYPOINT_PRECONF_COMMAND`` run an extra pre conf shell command after
   all pre conf commands.
-  ``ENTRYPOINT_POSTCONF_COMMAND`` run an extra post conf shell command after
   all post conf commands.
-  ``ENTRYPOINT_DEBUG`` enables debug logs.
-  ``ENTRYPOINT_RAW`` does not use logging to display pre and post conf
   commands. This can be useful if output is serialized.
-  ``ENTRYPOINT_DISABLE_RELOAD`` disable reload system even if it is enabled
   in ``entrypoint-config.yml``.
-  ``ENTRYPOINT_USER`` overrides ``user`` in config.
-  ``ENTRYPOINT_GROUP`` overrides ``group`` in config.
