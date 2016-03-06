"Command object"
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from fnmatch import fnmatch


class Command(object):
    """This object handle command in dockerfile"""

    def __init__(self, command, config, args):
        self.config = config
        self.args = args
        self.command = command
        self.env = os.environ

    def _clean_links_env(self):
        # TODO: that Looks too much complicated
        all_link_names = []

        def is_link_env(env, links):
            for link in links:
                patterns = [
                    '{}_NAME'.format(link),
                    '{}_PORT_*'.format(link),
                    '{}_ENV_*'.format(link),
                ]
                for patt in patterns:
                    if fnmatch(link, patt):
                        return True
            return False

        for link in self.config.links.all:
            all_link_names.extend(link.names)
        self.env = {env: val for env, val in os.environ.items()
                    if not is_link_env(env, all_link_names)}

    @property
    def is_handled(self):
        subcom = self.config.subcommands
        if not self.args or self.args[0] == self.command or \
                [p for p in subcom if fnmatch(self.args[0], p)]:
            return True
        return False

    def run(self):
        if not self.is_handled:
            os.execvpe(self.args[0], self.args, self.env)
        if os.getuid() is 0:
            os.setgid(self.config.group)
            os.setuid(self.config.user)
        if self.config.clean_env:
            self._clean_links_env()
        for item in self.config.secret_env:
            if item in os.environ:
                del(self.env[item])
        subcom = self.config.subcommands
        if not self.args or \
                [p for p in subcom if fnmatch(self.args[0], p)]:
            self.args.insert(0, self.command)
        os.execvpe(self.args[0], self.args, self.env)
