"Tests for runner"
import os
from multiprocessing import Process

from pyentrypoint import Entrypoint


def compare_timestamps():
    with open('/tmp/timestamp1', 'r') as f:
        first = int(f.readline())
    with open('/tmp/timestamp2', 'r') as f:
        second = int(f.readline())
    return second - first


def test_runner():
    run = [
        (Process(target=Entrypoint(
            conf='configs/runner.yml',
            args=['sleep', '5']).launch), 0, 0),
    ]

    for proc, uid, gid in run:
        proc.start()
        proc.join()
        assert compare_timestamps() > 3
        assert os.stat('/tmp/timestamp1').st_uid == uid
        assert os.stat('/tmp/timestamp1').st_gid == gid


def test_runner_parallele():
    run = [
        (Process(target=Entrypoint(
            conf='configs/runner_parallele.yml',
            args=['sleep', '5']).launch), 0, 0),
    ]

    for proc, uid, gid in run:
        proc.start()
        proc.join()
        assert compare_timestamps() < 1
        assert os.stat('/tmp/timestamp1').st_uid == uid
        assert os.stat('/tmp/timestamp1').st_gid == gid
