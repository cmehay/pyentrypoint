"""
    Configuration
"""
import os
from grp import getgrnam
from io import open
from pwd import getpwnam

from command import Command
from docker_links import DockerLinks
from links import Links
from six import string_types
from yaml import load
from yaml import Loader


class Config(object):

    """Get entrypoint config"""

    # Config file should always be in WORKDIR and named
    # entrypoint-config.yml
    _config_file = 'entrypoint-config.yml'

    def _return_item_lst(self, item):
        """Return item as a list"""
        if item in self._config:
            if isinstance(self._config[item], string_types):
                return [self._config[item]]
            return self._config[item]
        return []

    def __init__(self, args=[]):
        self._config = {}
        self._args = []
        self._links = None
        if not os.path.isfile(self._config_file):
            return
        try:
            with open(self._config_file) as f:
                self._config = load(stream=f, Loader=Loader)
        except Exception as err:
            # TODO: logger
            print(err)
        self._args = args

    @property
    def as_config(self):
        "Has config file provided."
        return len(self._config) is not 0

    @property
    def command(self):
        "Main command to run."
        cmd = self._args[0] if self._args else ''
        for key in ['command', 'cmd']:
            if key in self._config:
                cmd = self._config[key]
        return Command(cmd, self, self._args)

    @property
    def subcommands(self):
        """Subcommands to handle as arguments."""
        rtn = self._return_item_lst('subcommands')
        if not rtn:
            return ['-*']
        return rtn

    @property
    def user(self):
        "Unix user or uid to run command."
        if 'user' in self._config:
            if isinstance(self._config['user'], int):
                return self._config['user']
            return getpwnam(name=self._config['user']).pw_uid
        return os.getuid()

    @property
    def group(self):
        "Unix group or gid to run command."
        if 'group' in self._config:
            if isinstance(self._config['user'], int):
                return self._config['user']
            return getgrnam(name=self._config['user']).pw_gid
        return os.getgid()

    @property
    def config_files(self):
        "List of template config files."
        return self._return_item_lst('config_files')

    @property
    def secret_env(self):
        """Environment variables to delete before running command."""
        return self._return_item_lst('secret_env')

    @property
    def links(self):
        """Links configs singleton."""
        if self._links:
            return self._links
        if 'links' not in self._config:
            self._links = Links(links=DockerLinks())
            return self._links
        self._links = Links(config=self._config['links'], links=DockerLinks())
        for name in self._config['links']:
            self._links._add_name(name)
        return self._links

    @property
    def pre_conf_commands(self):
        """Return list of preconf commands"""
        if 'pre_conf_commands' in self._config:
            return self._return_item_lst(self._config['pre_conf_command'])

    @property
    def post_conf_commands(self):
        """Return list of postconf commands"""
        if 'post_conf_commands' in self._config:
            return self._return_item_lst(self._config['post_conf_command'])

    @property
    def clean_env(self):
        """Clean env from linked containers before running command"""
        if 'clean_env' in self._config:
            return bool(self._config['clean_env'])
        return True

    @property
    def debug(self):
        """Enable debug logs."""
        if 'debug' in self._config:
            return bool(self._config['debug'])
        return False
