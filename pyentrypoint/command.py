"Command object"
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from fnmatch import fnmatch

from .logs import Logs
from .runner import Runner


class Command(object):
    """This object handle command in dockerfile"""

    def __init__(self, command, config, args):
        self.config = config
        self.args = args
        self.command = command
        self.env = os.environ
        self.log = Logs().log
        self.log.debug('Handled command is: {cmd}'.format(cmd=self.command))
        self.log.debug('Arguments are: "{args}"'.format(
            args='" "'.join(self.args)
        ))
        self.runner = Runner(config=self.config,
                             cmds=self.config.post_run_commands)

    def _rm_dockerenv(self):
        """Delete '/.dockerenv' and '/.dockerinit' files"""
        files = ['/.dockerenv', '/.dockerinit']
        for f in files:
            if os.path.isfile(f):
                self.log.debug('Removing {file} file'.format(file=f))
                os.unlink(f)

    def _clean_links_env(self):
        # TODO: that Looks too much complicated
        all_link_names = []

        def is_link_env(env, links):
            for link in links:
                patterns = [
                    '{}_NAME'.format(link.upper()),
                    '{}_PORT_*'.format(link.upper()),
                    '{}_ENV_*'.format(link.upper()),
                ]
                for patt in patterns:
                    if fnmatch(env, patt):
                        return True
            return False

        for link in self.config.links.all:
            all_link_names.extend(link.names)
        self.env = {env: val for env, val in os.environ.items()
                    if not is_link_env(env, all_link_names)}

    def _clean_secret_env(self):
        to_del = []
        for key in self.env:
            for item in self.config.secret_env:
                if fnmatch(key, item):
                    self.log.debug("Secret env '{item}' match '{key}'".format(
                        item=item,
                        key=key,
                    ))
                    to_del.append(key)

        for item in to_del:
            del(self.env[item])

    @property
    def is_handled(self):
        subcom = self.config.subcommands
        if not self.args or self.args[0] == self.command or \
                [p for p in subcom if fnmatch(self.args[0], p)]:
            self.log.debug("Command is handled")
            return True
        self.log.debug("Command is not handled")
        return False

    def _exec(self):
        self.log.debug('Now running: "{args}"'.format(
            args='" "'.join(self.args)
        ))
        if not self.args[0]:
            raise Exception('Nothing to run')
        os.execvpe(self.args[0], self.args, self.env)

    def _run_reloader(self):
        if self.config.reload:
            self.log.debug('Launching reloader process')
            self.config.reload.run_in_process()

    def _run_post_commands(self):
        if self.config.post_run_commands:
            self.log.debug('Running post run commands')
            self.runner.run_in_process()

    def run(self):
        if not self.is_handled:
            self._exec()
        self._rm_dockerenv()
        if os.getuid() is 0:
            os.setgid(self.config.group)
            os.setuid(self.config.user)
            self.log.debug('Set uid {uid} and gid {gid}'.format(
                uid=self.config.user,
                gid=self.config.group,
            ))
        if self.config.clean_env:
            self._clean_links_env()
        self._clean_secret_env()
        subcom = self.config.subcommands
        if not self.args or \
                [p for p in subcom if fnmatch(self.args[0], p)]:
            self.args.insert(0, self.command)
        self._run_reloader()
        self._run_post_commands()
        self._exec()
