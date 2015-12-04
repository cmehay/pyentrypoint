"""
    Configuration
"""

import fnmatch
import os
from grp import getgrnam
from io import open
from pwd import getpwnam

from six import string_types

from docker_links import DockerLinks
from pyyaml import Loader, load


class Link(object):

    """Link object"""

    def __init__(self, ip, env, port, protocol, names):
        self.ip = ip
        self.env = env
        self.port = port
        self.protocol = protocol
        self.uri = '{protocol}://{ip}:{port}'.format(
            protocol=protocol,
            ip=ip,
            port=port,
        )
        self.names = tuple(names)


class Links(object):

    """Links embeder"""

    _links = []
    _conf = None

    def __init__(self, links={}, conf=None):
        if len(links) is 0:
            pass

        for ip, link in links.links.items():
            for port, protocol in link["ports"].items():
                self._links.append(Link(ip=ip,
                                        env=link['environment'],
                                        port=port,
                                        protocol=protocol['protocol'],
                                        names=link['names']))

        self._conf = conf

    def _get_link(self, name):
        conf = self._conf[name]
        links = self._links
        for link in links:
            if 'port' in conf and link.port is not conf['port']:
                links.pop(link)
                continue
            if 'name' in conf \
                    and len(fnmatch.filter(link.names, conf['name'])) is 0:
                links.pop(link)
                continue
            if 'protocol' in conf and link.protocol is not conf['protocol']:
                links.pop(link)

        return tuple(links)

    @classmethod
    def _add_name(cls, name):
        setattr(cls, name, property(lambda self: self._get_link(name)))

    @property
    def all(self):
        """all returns tuple of all Link objects"""
        return tuple(self._links)


class Config(object):

    """Get entrypoint config"""

    # Config file should always be in WORKDIR and named
    # entrypoint-config.yml
    _config_file = 'entrypoint-config.yml'

    _config = {}

    def _return_item_lst(self, item):
        """Return item as a list"""
        if item in self._config:
            if isinstance(self._config[item], string_types):
                return [self._config[item]]
            return self._config[item]
        return []

    def __init__(self):
        if not os.path.isfile(self._config_file):
            return
        try:
            with open(self._config_file) as f:
                self._config = load(stream=f, Loader=Loader)
        except Exception as err:
            # TODO: logger
            print(err)

    @property
    def as_config(self):
        "Has config file provided."
        return len(self._config) is not 0

    @property
    def command(self):
        "Main command to run."
        if 'command' in self._config:
            return self._config['command']
        elif 'cmd' in self._config:
            return self._config['cmd']

    @property
    def subcommands(self):
        """Subcommands to handle as arguments."""
        return self._return_item_lst('subcommands')

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
        """Links configs."""
        links = DockerLinks()
        if 'links' not in self._config:
            return Links(links=links)
        links = Links(links=links, config=self._config['links'])
        for name in self._config['links']:
            links._add_name(name)
        return links

    @property
    def pre_conf_command(self):
        """Return Exec object of preconf command"""
        if 'pre_conf_command' in self._config:
            return self._config['pre_conf_command']

    @property
    def post_conf_command(self):
        """Return Exec object of preconf command"""
        if 'post_conf_command' in self._config:
            return self._config['post_conf_command']

    @property
    def debug(self):
        """Enable debug logs."""
        if 'debug' in self._config:
            return bool(self._config['debug'])
        return False
