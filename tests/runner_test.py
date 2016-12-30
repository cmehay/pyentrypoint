"Tests for runner"
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from multiprocessing import Process

from pyentrypoint import Entrypoint


def test_runner():
    run = [
        (Process(target=Entrypoint(
            conf='configs/runner.yml',
            args=['sleep', '5']).launch),
         '/tmp/runner_test', 0, 0),
    ]

    for proc, test, uid, gid in run:
        proc.start()
        proc.join()
        with open(test, 'r') as f:
            assert f.readline().startswith('OK')
        assert os.stat(test).st_uid == uid
        assert os.stat(test).st_gid == gid
