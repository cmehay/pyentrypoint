#!/usr/bin/env python

"""
    Smart docker-entrypoint
"""

import fnmatch
import os
from grp import getgrnam
from io import open
from pwd import getpwnam

from six import string_types
from twiggy import levels, log, quickSetup

from docker_links import DockerLinks
from pyyaml import Loader, load

from config import Config


class Entrypoint(object):

    """Entrypoint class."""

    def _set_logguer(self):
        quickSetup(min_level=levels.INFO)
        self.log = log.name('entrypoint')

    def __init__(self):
        self._set_logguer()
        try:
            self.config = Config()
        except Exception as err:
            self.log.error(err)
        if self.config.debug:
            quickSetup(min_level=levels.DEBUG)

        print(vars(self.config))
        print(vars(self.config.links))


Entrypoint()
