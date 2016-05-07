"""
    Get log object
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from colorlog import ColoredFormatter


class Switch(object):
    """Just a mutable boolean to fool init Logs method"""

    def __init__(self, b=True):
        self._v = b

    def __eq__(self, val):
        return self._v == val

    def __bool__(self):
        return self._v

    def __nonzero__(self):
        "Python 2 bool"
        return self._v

    def true(self):
        self._v = True

    def false(self):
        self._v = False


class Logs(object):
    """Get a logguer"""

    lvl = logging.INFO

    #  As log attribute is muttable, we can use method to change
    # log level accross instances
    log = logging.getLogger('Entrypoint')

    # Just a trick to avoid multiple formatter in logging instance
    _switch = Switch(False)

    def __init__(self):
        if bool(self._switch):
            # Log is static, don't override it
            return None
        formatter = ColoredFormatter(
            "%(name)s %(log_color)s%(levelname)-8s%(reset)s %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',
            }
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(self.lvl)

        self._switch.true()

    @classmethod
    def set_debug(cls):
        """Set log level to debug"""
        cls.lvl = logging.DEBUG
        cls.log.setLevel(cls.lvl)

    @classmethod
    def set_info(cls):
        """Set log level to info"""
        cls.lvl = logging.INFO
        cls.log.setLevel(cls.lvl)

    @classmethod
    def set_warning(cls):
        """Set log level to info"""
        cls.lvl = logging.WARNING
        cls.log.setLevel(cls.lvl)

    @classmethod
    def set_critical(cls):
        """Set log level to info"""
        cls.lvl = logging.CRITICAL
        cls.log.setLevel(cls.lvl)
