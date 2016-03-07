"""
    Container object handle a single container link
"""
from __future__ import absolute_import
from __future__ import unicode_literals


class Container(object):

    """Container handles a single container link"""

    def __init__(self, ip, env, names, id, links=None):
        self.ip = ip
        self.environ = env
        self.names = names
        self.id = id
        self._set_links(links)

    def _set_links(self, links):
        lst = []
        if not links:
            self.links = tuple()
        for link in links:
            if link.ip == self.ip:
                lst.append(link)
        self.links = tuple(lst)
