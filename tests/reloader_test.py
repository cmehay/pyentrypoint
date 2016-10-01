"Tests for reloader"
from __future__ import absolute_import
from __future__ import unicode_literals


try:
    # Python2
    import mock
except ImportError:
    # Python3
    from unittest import mock

from pyentrypoint import Entrypoint

import subprocess

from signal import SIGHUP

from time import sleep


def test_reloader():

    with mock.patch('os.kill') as os_kill:
        entry = Entrypoint(conf='configs/reloader/reloader.yml')
        entry.apply_conf()
        entry.config.reload.run(ret=True)
        subprocess.check_call(['touch', '/tmp/reload'])
        sleep(1)
        entry.config.reload.stop()
        os_kill.assert_called_once_with(1, SIGHUP)


def test_reloader_custom():

    with mock.patch('os.kill') as os_kill:
        entry = Entrypoint(conf='configs/reloader/reloader_config.yml')
        entry.apply_conf()
        entry.run_pre_conf_cmds()
        entry.config.reload.run(ret=True)
        subprocess.check_call(['touch', '/tmp/reload', '/tmp/reload_custom'])
        sleep(1)
        entry.config.reload.stop()
        os_kill.assert_called_once_with(1, SIGHUP)
