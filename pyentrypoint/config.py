"""
    Configuration object
"""
import os
from distutils.util import strtobool
from fnmatch import fnmatch
from grp import getgrnam
from io import open
from pwd import getpwnam

from six import string_types
from yaml import safe_load

from .command import Command
from .constants import ENTRYPOINT_FILE
from .docker_links import DockerLinks
from .links import Links
from .logs import Logs
from .reloader import Reloader

__all__ = ['Config']


def envtobool(key, default):
    return bool(strtobool(os.environ.get(key, str(default))))


class ConfigMeta(object):

    def _return_item_lst(self, item):
        """Return item as a list"""
        if item in self._config:
            if isinstance(self._config[item], string_types):
                return [self._config[item]]
            return self._config[item]
        return []

    def get_templates(self):
        """Returns iterator of tuple (template, config_file)"""
        config_files = self.config_files
        if isinstance(config_files, list):
            for item in config_files:
                if isinstance(item, string_types):
                    template = item
                    outfile = item[:-4] if item.endswith('.tpl') else item
                if isinstance(item, dict):
                    template = list(item.keys())[0]
                    outfile = item[template]
                yield (template, outfile)
        else:
            raise Exception("config_files setup missformated.")

    def get_reloader(self):
        """Setup and get reloader"""
        config_files = [file[1] for file in self.get_templates()]
        reload = self._config['reload']
        if isinstance(reload, bool):
            return Reloader(files=config_files)
        if isinstance(reload, dict):
            signal = reload.get('signal', 'SIGHUP')
            watch_config_files = bool(reload.get('watch_config_files'))
            files = reload.get('files', [])
            if not isinstance(files, list):
                raise Exception('Reload files is not a list')
            if watch_config_files:
                files.extend(config_files)
            return Reloader(files=files, sig=signal)

    def _check_config(self):
        for key in self._config:
            if not hasattr(Config, key) or key == '__init__':
                self.log.warning(
                    '"{key}" is not a valid option'.format(key=key)
                )

    def _get_from_env(self, env, key):
        val = os.environ.get(env, None)
        if val is None:
            return None
        try:
            val = int(val)
        except ValueError:
            pass
        self._config[key] = val

    def set_to_env(self):
        self.log.debug('Add conf to environment')
        for attr in [a for a in dir(self) if not a.startswith('_')]:
            setup = getattr(self, attr)
            env = 'ENTRYPOINT_{attr}'.format(attr=attr.upper())
            if type(setup) is bool and setup:
                self.log.debug('set env {env} with "true"'.format(
                    env=env
                ))
                os.environ[env] = 'true'
            if type(setup) is int or type(setup) is str:
                if env not in os.environ:
                    self.log.debug('set env {env} with "{val}"'.format(
                        env=env,
                        val=str(setup),
                    ))
                    os.environ[env] = str(setup)


class Config(ConfigMeta):

    """
    Get entrypoint config

    Parse entrypoint-config.yml

    Config file should always be in WORKDIR and named entrypoint-config.yml
    """

    def __init__(self, conf=ENTRYPOINT_FILE, args=[]):
        self._config = {}
        self.log = Logs().log
        self._args = args
        self._links = None
        self._command = None
        self._reload = None
        self._config_file = conf
        if not os.path.isfile(self._config_file):
            self.log.critical('Entrypoint config file does not provided')
            return
        with open(self._config_file) as f:
            self._config = safe_load(stream=f)
        self._check_config()

    @property
    def has_config(self):
        "Has config file provided."
        return len(self._config) != 0

    @property
    def commands(self):
        "Handled commands"
        rtn = self._return_item_lst('commands')
        return rtn

    @property
    def command(self):
        "Main command to run."
        if self._command:
            return self._command
        cmd = self._args[0] if self._args else ''
        if 'commands' in self._config:
            commands = self._return_item_lst('commands')
            if [p for p in commands if fnmatch(self._args[0], p)]:
                self._command = Command(cmd, self, self._args)
                return self._command
        for key in ['command', 'cmd']:
            if key in self._config:
                self.log.warning(
                    '"command" is deprecated, use "commands" instead',
                )
                cmd = self._config[key]
        self._command = Command(cmd, self, self._args)
        return self._command

    @property
    def subcommands(self):
        """Subcommands to handle as arguments."""
        rtn = self._return_item_lst('subcommands')
        if rtn:
            self.log.warning(
                '"subcommands" is deprecated, '
                'subcommands will not be handled anymore.',
            )
            if self.commands:
                self.log.warning(
                    '"subcommands" is ignored as long "commands" in present',
                )
            return rtn
        else:
            return ['-*']

    @property
    def user(self):
        "Unix user or uid to run command."
        self._get_from_env(env='ENTRYPOINT_USER', key='user')
        if 'user' in self._config:
            if isinstance(self._config['user'], int):
                return self._config['user']
            return getpwnam(self._config['user']).pw_uid
        return os.getuid()

    @property
    def group(self):
        "Unix group or gid to run command."
        self._get_from_env(env='ENTRYPOINT_GROUP', key='group')
        if 'group' in self._config:
            if isinstance(self._config['group'], int):
                return self._config['group']
            return getgrnam(self._config['group']).gr_gid
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
        return self._return_item_lst('pre_conf_commands')

    @property
    def post_conf_commands(self):
        """Return list of postconf commands"""
        return self._return_item_lst('post_conf_commands')

    @property
    def post_run_commands(self):
        """Return list of post run commands"""
        return self._return_item_lst('post_run_commands')

    @property
    def reload(self):
        """Return Reloader object if reload is set"""

        if self._reload:
            return self._reload
        if (not self._config.get('reload') or
                envtobool('ENTRYPOINT_DISABLE_RELOAD', False)):
            return None
        self._reload = self.get_reloader()
        return self._reload

    @property
    def clean_env(self):
        """Clean env from linked containers before running command"""
        if 'clean_env' in self._config:
            return bool(self._config['clean_env'])
        return True

    @property
    def remove_dockerenv(self):
        """Remove dockerenv and dockerinit files"""
        if 'remove_dockerenv' in self._config:
            return bool(self._config['remove_dockerenv'])
        return True

    @property
    def debug(self):
        """Enable debug logs."""
        if envtobool('ENTRYPOINT_DEBUG', False):
            return True
        if 'debug' in self._config:
            return bool(self._config['debug'])
        return False

    @property
    def quiet(self):
        """Disable logging"""
        if self.debug:
            return False
        if envtobool('ENTRYPOINT_QUIET', False):
            return True
        return bool(self._config.get('quiet', False))

    @property
    def is_disabled(self):
        """Return if service is disabled using environment"""
        return envtobool('ENTRYPOINT_DISABLE_SERVICE', False)

    @property
    def should_config(self):
        """Check environment to tell if config should apply anyway"""
        return envtobool('ENTRYPOINT_FORCE', False)

    @property
    def raw_output(self):
        """Check if command output should be displayed using logging or not"""
        if envtobool('ENTRYPOINT_RAW', False):
            return True
        return bool(self._config.get('raw_output', False))
