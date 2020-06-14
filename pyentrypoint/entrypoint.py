#!/usr/bin/env python
"""
    Smart docker-entrypoint
"""
import json
import os
from sys import argv
from sys import exit

import toml
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader

from .config import Config
from .config import envtobool
from .configparser import ConfigParser
from .constants import ENTRYPOINT_FILE
from .docker_links import DockerLinks
from .logs import Logs
from .runner import Runner

__all__ = ['Entrypoint', 'main']


class Entrypoint(object):

    """Entrypoint class."""

    def _set_logguer(self):
        self.log = Logs().log

    def __init__(self, conf=ENTRYPOINT_FILE, args=[]):
        self._set_logguer()
        if os.environ.get('ENTRYPOINT_CONFIG'):
            conf = os.environ['ENTRYPOINT_CONFIG']
        try:
            self.config = Config(conf=conf, args=args)
        except Exception as err:
            self.log.error(err)
            self.log.critical('Fail to initialize config, exiting now')
            exit(1)
        else:
            if self.config.debug:
                Logs.set_debug()
            if self.config.quiet:
                Logs.set_critical()
        self.args = args
        self.runner = Runner(config=self.config)

    @property
    def is_handled(self):
        """Is command handled by entrypoint"""
        return self.config.command.is_handled

    @property
    def is_disabled(self):
        """Return if service is disabled using environment"""
        return self.config.is_disabled

    @property
    def should_config(self):
        """Check environment to tell if config should apply anyway"""
        return self.config.should_config

    @property
    def raw_output(self):
        """Check if command output should be displayed using logging or not"""
        return self.config.raw_output

    def exit_if_disabled(self):
        """Exist 0 if service is disabled"""
        if not self.config.is_disabled:
            return

        self.log.warning("Service is disabled by 'ENTRYPOINT_DISABLE_SERVICE' "
                         "environement variable... exiting with 0")
        exit(0)

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
                                    json=json,
                                    yaml=yaml,
                                    toml=toml,
                                    ConfigParser=ConfigParser,
                                    envtobool=envtobool,
                                    containers=DockerLinks().to_containers()))

    def run_set_enviroment(self):
        for set_env in self.config.set_environment:
            if not isinstance(set_env, dict) and not len(set_env) == 1:
                raise Exception("set_environment is miss configured, "
                                "please check syntax in entrypoint config")
            env, cmd = next(((e, c) for e, c in set_env.items()))
            self.log.debug(f'Set environment variable {env}')
            os.environ[env] = self.runner.run_cmd(cmd, stdout=True)

    def run_pre_conf_cmds(self):
        for cmd in self.config.pre_conf_commands:
            self.runner.run_cmd(cmd)
        if os.environ.get('ENTRYPOINT_PRECONF_COMMAND'):
            self.runner.run_cmd(os.environ['ENTRYPOINT_PRECONF_COMMAND'])

    def run_post_conf_cmds(self):
        for cmd in self.config.post_conf_commands:
            self.runner.run_cmd(cmd)
        if os.environ.get('ENTRYPOINT_POSTCONF_COMMAND'):
            self.runner.run_cmd(os.environ['ENTRYPOINT_POSTCONF_COMMAND'])

    def launch(self):
        self.config.command.run()


def main(argv):
    argv.pop(0)
    entry = Entrypoint(args=argv)
    try:
        entry.exit_if_disabled()
        if not entry.is_handled and not entry.should_config:
            entry.log.warning("Running command without config")
            entry.launch()
        entry.config.set_to_env()
        entry.log.debug("Starting config")
        entry.run_set_enviroment()
        entry.run_pre_conf_cmds()
        entry.apply_conf()
        entry.run_post_conf_cmds()
        entry.launch()
    except Exception as e:
        entry.log.error(str(e))
        exit(1)


if __name__ == '__main__':
    main(argv)
