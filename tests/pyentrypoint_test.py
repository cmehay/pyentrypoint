# Tests using pytest
from __future__ import absolute_import
from __future__ import unicode_literals

import fnmatch
import os
from multiprocessing import Process

from yaml import load
from yaml import Loader

from pyentrypoint import DockerLinks
from pyentrypoint import Entrypoint

LINKS = [
    'test1',
    'test2',
    'test3',
    'test4',
]


def test_all_links():
    links = DockerLinks()
    all_links = links.links()

    assert len(all_links) == 4
    for _, item in all_links.items():
        assert len(set(item["names"]).intersection(LINKS))


def test_filtering():
    links = DockerLinks()
    test1 = links.links("test1")

    assert len(test1) == 1

    test2_and_3 = links.links("test2", "test3")

    assert len(test2_and_3) == 2

    test4_and_5 = links.links("test4", "notexist")
    assert len(test4_and_5) == 1

    test5 = links.links("notexist")
    assert len(test5) == 0


def test_env():
    links = DockerLinks()
    env = links.links("test1", "test3")

    for _, item in env.items():
        assert item["environment"]["FOO"] == "bar"


def test_ports():
    links = DockerLinks()

    ports = links.links('test1', 'test2')

    for _, item in ports.items():
        if 'test1' in item["names"]:
            assert item["ports"]["800"]['protocol'] == 'tcp'
            assert item["ports"]["8001"]['protocol'] == 'udp'
        else:
            assert item["ports"]["800"]['protocol'] == 'udp'
            assert item["ports"]["8001"]['protocol'] == 'tcp'


def test_entrypoint_links():
    entry = Entrypoint(conf='configs/base.yml')
    links = entry.config.links

    assert len(links.all) == 4

    assert len(links.test1) == 2

    assert links.test2_800.port == 800


def test_containers():
    links = DockerLinks()
    ctns = links.to_containers()

    assert len(ctns) == 4

    for ctn in ctns:
        if 'test1' in ctn.names:
            assert ctn.environ['FOO'] == 'bar'
            assert len(ctn.links) == 2
        if 'test2' in ctn.names:
            assert len(ctn.links) == 2
        if 'test3' in ctn.names:
            assert ctn.environ['FOO'] == 'bar'
            assert len(ctn.links) == 0
        if 'test4' in ctn.names:
            assert len(ctn.links) == 0

        # Test sorted names
        int(ctn.names[-1], base=16)


def test_templates():
    entry = Entrypoint(conf='configs/base.yml')

    conf = entry.config

    entry.apply_conf()

    with open(conf.config_files[0], mode='r') as r:
        test = load(stream=r, Loader=Loader)

    assert len(set(test['All links'])) == 4
    assert len(set(test['All links 1'])) == 2
    assert len(set(test['All links 2'])) == 2

    assert fnmatch.fnmatch(test['Links 2 800'][0], 'udp://*:800')

    # test environment
    assert test['All environ']['FOO'] == 'bar'
    assert test['All links 2 environ']['FOO'] == 'bar'

    test_names = [
        'test1',
        'test2',
        'test3',
        'test4',
    ]

    # test names
    for test_name in test_names:
        assert test_name in test['All names']


def test_conf_commands():
    entry = Entrypoint(conf='configs/base.yml')

    for cmd in entry.config.pre_conf_commands:
        entry.run_conf_cmd(cmd)
    for cmd in entry.config.post_conf_commands:
        entry.run_conf_cmd(cmd)

    with open('/tmp/OK') as f:
        assert f.readline().startswith('TEST')

    with open('/tmp/OKOK') as f:
        assert f.readline().startswith('TEST2')

    with open('/tmp/OKOKOK') as f:
        assert f.readline().startswith('TEST3')


def test_command():
    run = [
        #  ((Process instance), (file to check), (uid), (gid))
        (Process(target=Entrypoint(
            conf='configs/base.yml',
            args=['-c', 'echo OK > /tmp/CMD']).launch),
            '/tmp/CMD', 1000, 1000),
        (Process(target=Entrypoint(
            conf='configs/base.yml',
            args=['bash', '-c', 'echo ${SECRET}OK > /tmp/CMD2']).launch),
            '/tmp/CMD2', 1000, 1000),
        (Process(target=Entrypoint(
            conf='configs/usernames.yml',
            args=['bash', '-c', 'echo OK > /tmp/CMD3']).launch),
            '/tmp/CMD3', 33, 33),
        (Process(target=Entrypoint(
            conf='configs/unhandled.yml',
            args=['bash', '-c', 'echo OK > /tmp/CMD4']).launch),
            '/tmp/CMD4', 0, 0),
    ]

    for proc, test, uid, gid in run:
        proc.start()
        proc.join()
        with open(test) as f:
            assert f.readline().startswith('OK')
        assert os.stat(test).st_uid == uid
        assert os.stat(test).st_gid == gid
