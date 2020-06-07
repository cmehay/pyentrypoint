"Run commands"
from multiprocessing import Process
from subprocess import PIPE
from subprocess import Popen

from .logs import Logs


class Runner(object):
    'This object run commands'

    def __init__(self, config, cmds=[]):
        self.log = Logs().log
        self.cmds = cmds
        self.raw_output = config.raw_output
        self.parallele_run = config.run_post_commands_in_parallele
        self.stdout_cb = self.log.info if not self.raw_output else print
        self.stderr_cb = self.log.warning if not self.raw_output else print

    def stdout(self, output):
        for line in output:
            self.stdout_cb(line.rstrip())

    def stderr(self, output):
        for line in output:
            self.stderr_cb(line.rstrip())

    def stream_output(self, proc):
        display_stdout = Process(target=self.stdout, args=(proc.stdout,))
        display_stdout.start()
        display_stderr = Process(target=self.stderr, args=(proc.stderr,))
        display_stderr.start()

    def run_cmd(self, cmd, stdout=False):
        self.log.debug('run command: {}'.format(cmd))
        with Popen(cmd,
                   shell=True,
                   stdout=PIPE,
                   stderr=PIPE,
                   universal_newlines=True) as proc:
            if stdout:
                output, _ = proc.communicate()
            else:
                self.stream_output(proc)
        if proc.returncode:
            raise Exception('Command exit code: {}'.format(proc.returncode))
        if stdout and output:
            return output

    def run(self):
        for cmd in self.cmds:
            self.run_cmd(cmd)

    def run_in_process(self):
        if self.parallele_run:
            return self.run_in_parallele()
        self.proc = Process(target=self.run)
        self.proc.start()

    def run_in_parallele(self):
        for cmd in self.cmds:
            self.proc = Process(target=self.run_cmd,
                                args=[cmd])
            self.proc.start()
