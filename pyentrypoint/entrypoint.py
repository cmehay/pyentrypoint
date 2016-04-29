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

from .config import Config
from .constants import ENTRYPOINT_FILE
from .docker_links import DockerLinks
from .logs import Logs

__all__ = ['Entrypoint', 'main']


class Entrypoint(object):

    """Entrypoint class."""

    def _set_logguer(self):
        self.log = Logs().log

    def __init__(self, conf=ENTRYPOINT_FILE, args=[]):
        self._set_logguer()
        if 'ENTRYPOINT_CONFIG' in os.environ:
            conf = os.environ['ENTRYPOINT_CONFIG']
        try:
            self.config = Config(conf=conf, args=args)
        except Exception as err:
            self.log.error(err)
        if self.config.debug:
            Logs.set_debug()
        self.args = args

    @property
    def is_handled(self):
        """Is command handled by entrypoint"""
        return self.config.command.is_handled

    @property
    def should_config(self):
        """Check environment to tell if config should apply anyway"""
        return 'ENTRYPOINT_FORCE' in os.environ

    def apply_conf(self):
        """Apply config to template files"""
        env = Environment(loader=FileSystemLoader('/'))
        for template, conf_file in self.config.get_templates():
            temp = env.get_template(template)
            with open(conf_file, mode='w') as f:
                self.log.debug('Applying conf to {}'.format(conf_file))
                f.write(temp.render(config=self.config,
                                    links=self.config.links,
                                    env=os.environ,
                                    environ=os.environ,
                                    containers=DockerLinks().to_containers()))

    def run_conf_cmd(self, cmd):
        self.log.debug('run command: {}'.format(cmd))
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        def dispout(output, cb):
            enc = stdout.encoding or 'UTF-8'
            output = output.decode(enc).split('\n')
            l = len(output)
            for c, line in enumerate(output):
                if c + 1 == l and not len(line):
                    # Do not display last empty line
                    break
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
        if not entry.is_handled and not entry.should_config:
            entry.launch()
        entry.run_pre_conf_cmds()
        entry.apply_conf()
        entry.run_post_conf_cmds()
        entry.launch()
    except Exception as e:
        entry.log.error(str(e))


if __name__ == '__main__':
    main(argv)
