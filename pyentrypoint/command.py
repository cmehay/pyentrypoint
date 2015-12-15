"Command object"
import fnmatch
import os


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
                    if fnmatch.fnmatch(link, patt):
                        return True
            return False

        for link in self.config.links.all:
            all_link_names.extend(link.names)
        self.env = {env: val for env, val in os.environ.items()
                    if not is_link_env(env, all_link_names)}

    def run(self):
        if os.getuid() is 0:
            os.setuid(self.config.user)
            os.setgid(self.config.group)
        if self.config.clean_env:
            self._clean_links_env()
        for item in self.config.secret_env:
            if item in os.environ:
                del(self.env[item])
        if not self.args or \
                fnmatch.filter(self.config.subcommands, self.args[0]):
            args = self.args if self.args else [self.command]
            os.execvpe(self.command, args, os.environ)
        os.execvpe(args[0], args, os.environ)
