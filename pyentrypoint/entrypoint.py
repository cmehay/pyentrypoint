#!/usr/bin/env python
"""
    Smart docker-entrypoint
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from subprocess import PIPE
from subprocess import Popen
from sys import argv
from sys import stdout

from jinja2 import Environment
from jinja2 import FileSystemLoader
from twiggy import levels
from twiggy import log
from twiggy import quickSetup

from .config import Config
from .constants import ENTRYPOINT_FILE
from .docker_links import DockerLinks

__all__ = ['Entrypoint', 'main']


class Entrypoint(object):

    """Entrypoint class."""

    def _set_logguer(self):
        quickSetup(min_level=levels.INFO)
        self.log = log.name('entrypoint')

    def __init__(self, conf=ENTRYPOINT_FILE, args=[]):
        self._set_logguer()
        try:
            self.config = Config(conf=conf, args=args)
        except Exception as err:
            self.log.error(err)
        if self.config.debug:
            quickSetup(min_level=levels.DEBUG)
        self.args = args

    @property
    def is_handled(self):
        return self.config.command.is_handled

    def apply_conf(self):
        env = Environment(loader=FileSystemLoader('/'))
        for template in self.config.config_files:
            temp = env.get_template(template)
            with open(template, mode='w') as f:
                self.log.info('Applying conf to {}'.format(template))
                f.write(temp.render(config=self.config,
                                    links=self.config.links,
                                    env=os.environ,
                                    containers=DockerLinks().to_containers()))

    def run_conf_cmd(self, cmd):
        self.log.info('run command: {}'.format(cmd))
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        def dispout(output, cb):
            enc = stdout.encoding or 'UTF-8'
            output = output.decode(enc).split('\n')
            for line in output:
                cb(line)

        if out:
            dispout(out, self.log.info)
        if err:
            dispout(err, self.log.warning)
        if proc.returncode:
            raise Exception('Command exit code: {}'.format(proc.returncode))

    def run_pre_conf_cmds(self):
        for cmd in self.config.pre_conf_commands:
            self.run_conf_cmd(cmd)

    def run_post_conf_cmds(self):
        for cmd in self.config.post_conf_commands:
            self.run_conf_cmd(cmd)

    def launch(self):
        self.config.command.run()


def main(argv):
    argv.pop(0)
    entry = Entrypoint(args=argv)
    try:
        if not entry.is_handled:
            entry.launch()
        entry.run_pre_conf_cmds()
        entry.apply_conf()
        entry.run_post_conf_cmds()
        entry.launch()
    except Exception as e:
        entry.log.error(str(e))


if __name__ == '__main__':
    main(argv)
