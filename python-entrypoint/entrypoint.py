#!/usr/bin/env python

"""
    Smart docker-entrypoint
"""

from twiggy import levels, log, quickSetup

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
