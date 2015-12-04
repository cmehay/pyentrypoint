#!/usr/bin/env python

"""
    DockerLinks a kiss class which help to get links info in a docker
    container.
"""

import json
import os
import re


class DockerLinks(object):

    "List all links and return a dictionnary of ip addresses with \
        link names, environment, ports and protocols."

    def __init__(self):
        self._get_links()
        self._sort_names()

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def _get_links(self):
        self.all_links = {}
        # nb_args = len(args)
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
                # if nb_args and link_name not in args:
                #     continue
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
        for _, item in self.all_links.items():
            item["names"].sort()

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
