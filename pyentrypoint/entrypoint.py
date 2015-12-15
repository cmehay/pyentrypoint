#!/usr/bin/env python
"""
    Smart docker-entrypoint
"""
from subprocess import PIPE
from subprocess import Popen
from sys import argv

from command import Command
from config import Config
from jinja2 import Environment
from jinja2 import FileSystemLoader
from twiggy import levels
from twiggy import log
from twiggy import quickSetup


class Entrypoint(object):

    """Entrypoint class."""

    def _set_logguer(self):
        quickSetup(min_level=levels.INFO)
        self.log = log.name('entrypoint')

    def __init__(self, args=[]):
        self._set_logguer()
        try:
            self.config = Config()
        except Exception as err:
            self.log.error(err)
        if self.config.debug:
            quickSetup(min_level=levels.DEBUG)
        self.args = args

    def apply_conf(self):
        env = Environment(loader=FileSystemLoader('/'))
        for template in self.config.config_files:
            temp = env.get_template(template)
            with open(template, mode='w') as f:
                self.log.info('Applying conf to {}'.format(template))
                f.write(temp.render(config=self.config,
                                    links=self.config.links))

    def run_conf_cmd(self, cmd):
        self.log.info('run command: {}'.format(cmd))
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        self.log.info(out)
        self.log.warning(err)
        if proc.returncode:
            raise Exception('Command exit code: {}'.format(proc.returncode))

    def launch(self):
        self.args.pop(0)
        command = Command(self.config, self.args)
        command.run()


if __name__ == '__main__':
    entry = Entrypoint(argv)
    try:
        for cmd in entry.config.pre_conf_commands:
            entry.run_conf_cmd(cmd)
        entry.apply_conf()
        for cmd in entry.config.post_conf_commands:
            entry.run_conf_cmd(cmd)
        entry.launch()
    except Exception as e:
        print(e)
