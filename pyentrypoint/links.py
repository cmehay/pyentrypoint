"""
    Link handle a single link to another container, determined by his port
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import fnmatch

from six import viewitems

__all__ = ['Link', 'Links']


class Link(object):

    """Link object"""

    def __init__(self, ip, env, port, protocol, names):
        self.ip = ip
        self.environ = env
        self.port = int(port)
        self.protocol = protocol
        self.uri = '{protocol}://{ip}:{port}'.format(
            protocol=protocol,
            ip=ip,
            port=port,
        )
        self.names = tuple(names)

    def _filter_name(self, name):
        "return true if name match"
        return bool(fnmatch.filter(self.names, name))

    def _filter_port(self, port):
        "return true if port match"
        return int(port) == self.port

    def _filter_protocol(self, protocol):
        "return true if protocol match"
        return protocol == self.protocol

    def _filter_env(self, env):
        "return true if env match"
        if isinstance(env, dict):
            return viewitems(env) <= viewitems(self.environ)
        if isinstance(env, list):
            return bool([key for key in env if key in self.environ])
        return str(env) in self.environ


class Links(object):

    """Links embeder"""

    _conf = None
    _def_options = {'single': False,
                    'required': True}

    def __init__(self, config=None, links=None):
        if not links or len(links.links()) is 0:
            pass

        self._links = []
        for ip, link in links.links().items():
            for port, protocol in link["ports"].items():
                self._links.append(Link(ip=ip,
                                        env=link['environment'],
                                        port=int(port),
                                        protocol=protocol['protocol'],
                                        names=link['names']))

        self._conf = config

    def _get_link(self, name):
        config = self._conf[name]
        links = self._links
        options = dict(self._def_options)
        for key, val in config.items():
            if key in options:
                options[key] = val
                continue
            links = [link for link in links
                     if getattr(link, "_filter_{}".format(key))(val)]

        if options['required'] and len(links) is 0:
            raise Exception("No links was found for {name}".format(name=name))
        if options['single'] and len(links) > 1:
            raise Exception("Only one link should be provided for {name}"
                            .format(name=name))
        if options['single']:
            return links[0]
        return tuple(links)

    @classmethod
    def _add_name(cls, name):
        "Add method attribute name"
        setattr(cls, name, property(lambda self: self._get_link(name)))

    @property
    def all(self):
        """all returns tuple of all Link objects"""
        return tuple(self._links)
