.. pyentrypoint documentation master file, created by
   sphinx-quickstart on Thu Apr 28 23:51:03 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyentrypoint's documentation!
========================================

**pyentrypoint** is a tool written in ``Python`` to manage Docker
containers ``ENTRYPOINT``.

This tool avoids writing shell scripts to:

- Handle commands and sub commands
- Identify linked containers
- Auto configure container using `jinja2` templates
- Run commands before starting service
- Clean environment before running service
- Increase security by setuid/setgid service

Contents:

.. toctree::
   :maxdepth: 3

   installation
   config
   templates
   extra


Working examples
~~~~~~~~~~~~~~~~

-  `Tor hidden
   service <https://github.com/cmehay/docker-tor-hidden-service>`__


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
