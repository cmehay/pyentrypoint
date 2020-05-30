"Run commands"
from multiprocessing import Process
from subprocess import PIPE
from subprocess import Popen
from sys import stdout as stdoutput

from .logs import Logs


class Runner(object):
    'This object run commands'

    def __init__(self, config, cmds=[]):
        self.log = Logs().log
        self.cmds = cmds
        self.raw_output = config.raw_output

    def run_cmd(self, cmd, stdout=False):
        self.log.debug('run command: {}'.format(cmd))
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        def dispout(output, cb):
            enc = stdoutput.encoding or 'UTF-8'
            output = output.decode(enc).split('\n')
            lenght = len(output)
            for c, line in enumerate(output):
                if c + 1 == lenght and not len(line):
                    # Do not display last empty line
                    break
                cb(line)

        if err:
            display_cb = self.log.warning if not self.raw_output else print
            dispout(err, display_cb)
        if out:
            display_cb = self.log.info if not self.raw_output else print
            if stdout:
                return out.decode()
            dispout(out, display_cb)
        if proc.returncode:
            raise Exception('Command exit code: {}'.format(proc.returncode))

    def run(self):
        for cmd in self.cmds:
            self.run_cmd(cmd)

    def run_in_process(self):
        self.proc = Process(target=self.run)
        self.proc.start()
