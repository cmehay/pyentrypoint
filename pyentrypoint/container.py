"""
    Container object handle a single container link
"""


class Container(object):

    """Container handles a single container link"""

    ip = None
    environ = None
    names = None
    links = None

    def __init__(self, ip, env, names, links=None):
        self.ip = ip
        self.environ = env
        self.names = names
        self.links = self._set_links(links)

    def _set_links(self, links):
        lst = []
        for link in links:
            if link.ip == self.ip:
                lst.append(link)
        self.links = tuple(lst)
