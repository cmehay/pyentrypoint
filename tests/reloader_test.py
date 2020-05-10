"Tests for reloader"


try:
    # Python2
    import mock
except ImportError:
    # Python3
    from unittest import mock

import os

from pyentrypoint import Entrypoint

import subprocess

from signal import SIGHUP

from time import sleep

from commons import clean_env


def teardown_function(function):
    clean_env()


def _reloader_check(conf, command):
    entry = Entrypoint(conf=conf)
    entry.apply_conf()
    entry.config.reload.run(ret=True)
    subprocess.check_call(command)
    sleep(1)
    entry.config.reload.stop()


def test_reloader():

    if 'ENTRYPOINT_DISABLE_RELOAD' in os.environ:
        os.environ.pop('ENTRYPOINT_DISABLE_RELOAD')

    with mock.patch('os.kill') as os_kill:
        _reloader_check(conf='configs/reloader/reloader.yml',
                        command=['touch', '/tmp/reload'])
        os_kill.assert_called_once_with(1, SIGHUP)


def test_disabled_reloader():

    os.environ['ENTRYPOINT_DISABLE_RELOAD'] = 'true'

    with mock.patch('os.kill') as os_kill:
        entry = Entrypoint(conf='configs/reloader/reloader.yml')
        entry.apply_conf()
        assert entry.config.reload is None
        assert not os_kill.called


def test_reloader_custom():

    if 'ENTRYPOINT_DISABLE_RELOAD' in os.environ:
        os.environ.pop('ENTRYPOINT_DISABLE_RELOAD')

    subprocess.check_call(['mkdir', '-p', '/tmp/1', '/tmp/2'])
    subprocess.check_call(['touch', '/tmp/2/tmp.match'])

    with mock.patch('os.kill') as os_kill:
        _reloader_check(conf='configs/reloader/reloader_config.yml',
                        command=['touch', '/tmp/1/reload_custom'])
        # triggered twice because file creation
        os_kill.assert_called_with(1, SIGHUP)

    with mock.patch('os.kill') as os_kill:
        _reloader_check(conf='configs/reloader/reloader_config.yml',
                        command=['touch', '/tmp/2/tmp.match'])
        os_kill.assert_called_once_with(1, SIGHUP)

    with mock.patch('os.kill') as os_kill:
        _reloader_check(conf='configs/reloader/reloader_config.yml',
                        command=['touch', '/tmp/2/tmpnotmatch'])
        assert not os_kill.called
