#!/usr/bin/env python
"""
    DockerLinks a kiss class which help to get links info in a docker
    container.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import os
import re

from .container import Container
from .links import Links

__all__ = ['DockerLinks']


class DockerLinks(object):

    "List all links and return a dictionnary of ip addresses with \
        link names, environment, ports and protocols."

    _links = None
    _containers = None

    def __init__(self):
        self._get_links()
        self._sort_names()

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def _get_links(self):
        self.all_links = {}
        # Read hosts file
        with open('/etc/hosts') as hosts:
            for line in hosts:
                split = line.split()
                if len(split) < 3:
                    continue
                # Check if entry is a link
                link_ip = split[0]
                link_name_env = split[1].upper().replace('-', '_')
                link_names = split[1:]
                env_var = "{link_name}_NAME".format(link_name=link_name_env)
                # Check if ip is already in dict
                if link_ip in self.all_links:
                    names = self.all_links[link_ip]["names"]
                    self.all_links[link_ip]["names"] = \
                        list(set(link_names + names))
                    continue
                if env_var in os.environ:
                    self.all_links[link_ip] = {
                        "ports": _find_ports(link_name_env),
                        "environment": _find_env(link_name_env),
                        "names": link_names,
                    }

    def _sort_names(self):
        "Sort names by len and put hexa at the end of list"
        def test_split(name):
            "Select key found in env"
            return bool([key for key in os.environ
                         if key.startswith(name.upper().replace('-', '_'))])

        for _, item in self.all_links.items():
            names = [name for name in item["names"] if test_split(name)]
            hexa = [name for name in item["names"] if not test_split(name)]

            names.sort(key=len)
            hexa.sort()
            item["names"] = names
            item["id"] = hexa[0] if len(hexa) else ''

    def links(self, *args):
        "Return dictionnary of links in container"
        nb_args = len(args)
        if not nb_args:
            return self.all_links
        return {link: item for link, item in self.all_links.items()
                if len(set(item["names"]).intersection(args))}

    def to_json(self, *args):
        "Return json formated string of links in container"
        return (json.dumps(self.links(*args),
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': '),
                           )
                )

    def to_containers(self):
        "Return tuple of Container object"
        if self._containers:
            return self._containers
        ctn = []
        links = self.get_links()
        for ip, item in self.all_links.items():
            ctn.append(Container(ip=ip,
                                 env=item['environment'],
                                 names=item['names'],
                                 id=item['id'],
                                 links=links))
        self._containers = tuple(ctn)
        return self._containers

    def get_links(self):
        "Get all links object"
        if self._links:
            return self._links.all
        self._links = Links(links=self)
        return self._links.all


def _find_ports(link_name):
    rtn = {}
    p = re.compile('^{link}_PORT_(\d*)_(UDP|TCP)$'.format(link=link_name))
    for key in os.environ:
        m = p.match(key)
        if m:
            rtn[m.group(1)] = {
                "protocol": m.group(2).lower(),
            }
    return rtn


def _find_env(link_name):
    rtn = {}
    p = re.compile('^{link}_ENV_(.*)$'.format(link=link_name))
    for key, value in os.environ.items():
        m = p.match(key)
        if m:
            rtn[m.group(1)] = value
    return rtn


if __name__ == '__main__':
    links = DockerLinks()
    print(links.to_json())
