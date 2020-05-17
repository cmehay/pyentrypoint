# Tests using pytest
import fnmatch
import os
from multiprocessing import Process

import pytest
from commons import clean_env
from yaml import FullLoader
from yaml import load

from pyentrypoint import DockerLinks
from pyentrypoint import Entrypoint

LINKS = [
    'test1',
    'test2',
    'test3',
    'test4',
]


def teardown_function(function):
    clean_env()


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
        int(ctn.id, base=16)
        assert len(ctn.names[0]) <= len(ctn.names[1])


def test_templates():
    test_confs = ['configs/base.yml']
    for test_conf in test_confs:
        entry = Entrypoint(conf='configs/base.yml')

        conf = entry.config

        entry.apply_conf()

        for _, config_file in conf.get_templates():
            with open(config_file, mode='r') as r:
                test = load(stream=r, Loader=FullLoader)

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

            # test id
            for id in test['ID']:
                int(id, base=16)

            # test env
            assert test['ENV']['SECRET'] == 'nothing'
            assert test['ENVIRON']['SECRET'] == 'nothing'

            # test yaml
            assert test['YAML']['yaml'] == 'ok'

            # test json
            assert test['JSON']['json'] == 'ok'


def test_conf_commands():

    entry = Entrypoint(conf='configs/base.yml')

    checks = [
        ('/tmp/OK', 'TEST'),
        ('/tmp/OKOK', 'TEST2'),
        ('/tmp/OKOKOK', 'TEST3'),
        ('/tmp/OKOKOKOK', 'TEST4'),
        ('/tmp/OKOKOKOKOK', 'TEST5'),
        ('/tmp/user', '1000'),
        ('/tmp/group', '1000'),
        ('/tmp/debug', 'true'),
    ]

    os.environ['ENTRYPOINT_PRECONF_COMMAND'] = 'echo TEST4 > /tmp/OKOKOKOK'
    os.environ['ENTRYPOINT_POSTCONF_COMMAND'] = 'echo TEST5 > /tmp/OKOKOKOKOK'

    entry.config.set_to_env()
    entry.run_pre_conf_cmds()
    entry.run_post_conf_cmds()

    for filename, value in checks:
        with open(filename) as f:
            line = f.readline()
            print(line)
            assert line.startswith(value)


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
            '/tmp/CMD3', 1009, 1010),
        (Process(target=Entrypoint(
            conf='configs/unhandled.yml',
            args=['bash', '-c', 'echo OK > /tmp/CMD4']).launch),
            '/tmp/CMD4', 0, 0),
        (Process(target=Entrypoint(
            conf='/dontexist',
            args=['bash', '-c', 'echo OK > /tmp/CMD5']).launch),
            '/tmp/CMD5', 0, 0),
        (Process(target=Entrypoint(
            conf='configs/secret_env.yml',
            args=['bash', '-c', 'echo ${SECRET}OK > /tmp/CMD6']).launch),
            '/tmp/CMD6', 0, 0),
    ]

    for proc, test, uid, gid in run:
        proc.start()
        proc.join()
        with open(test, 'r') as f:
            assert f.readline().startswith('OK')
        assert os.stat(test).st_uid == uid
        assert os.stat(test).st_gid == gid
        assert not os.path.isfile('/.dockerenv')
        assert not os.path.isfile('/.dockerinit')


def test_config_file():
    os.environ['ENTRYPOINT_CONFIG'] = 'configs/base.yml'
    entry = Entrypoint()

    assert entry.config.has_config

    del os.environ['ENTRYPOINT_CONFIG']


def test_force_config():
    entry = Entrypoint()
    assert not entry.should_config

    os.environ['ENTRYPOINT_FORCE'] = 'True'
    assert entry.should_config

    del os.environ['ENTRYPOINT_FORCE']


def test_display_raw():
    entry = Entrypoint()
    assert not entry.raw_output

    os.environ['ENTRYPOINT_RAW'] = 'True'
    assert entry.raw_output

    del os.environ['ENTRYPOINT_RAW']


def test_debug_env():
    os.environ['ENTRYPOINT_DEBUG'] = 'true'
    entry = Entrypoint(conf='configs/empty.yml')

    assert entry.config.debug

    del os.environ['ENTRYPOINT_DEBUG']


def test_quiet_env():
    os.environ['ENTRYPOINT_QUIET'] = 'true'
    entry = Entrypoint(conf='configs/empty.yml')

    assert entry.config.quiet

    del os.environ['ENTRYPOINT_QUIET']


def test_user_env():
    os.environ['ENTRYPOINT_USER'] = '100'
    entry = Entrypoint(conf='configs/base.yml')

    assert entry.config.user == 100

    os.environ['ENTRYPOINT_USER'] = 'testuser'
    entry = Entrypoint(conf='configs/base.yml')

    assert entry.config.user == 1009

    del os.environ['ENTRYPOINT_USER']


def test_group_env():
    os.environ['ENTRYPOINT_GROUP'] = '100'
    entry = Entrypoint(conf='configs/base.yml')

    assert entry.config.group == 100

    os.environ['ENTRYPOINT_GROUP'] = 'testgroup'
    entry = Entrypoint(conf='configs/base.yml')

    assert entry.config.group == 1010

    del os.environ['ENTRYPOINT_GROUP']


def test_disabled_service():
    os.environ['ENTRYPOINT_DISABLE_SERVICE'] = 'true'
    entry = Entrypoint(conf='configs/base.yml')

    assert entry.is_disabled

    with pytest.raises(SystemExit):
        entry.exit_if_disabled()

    del os.environ['ENTRYPOINT_DISABLE_SERVICE']


def test_commands_handling():
    cat = Entrypoint(conf='configs/commands.yml', args=['cat', 'hello'])
    sleep = Entrypoint(conf='configs/commands.yml', args=['sleep', '1'])
    bash = Entrypoint(conf='configs/commands.yml', args=['bash'])
    zsh = Entrypoint(conf='configs/commands.yml', args=['zsh', '-c', 'exit'])
    empty = Entrypoint(conf='configs/empty.yml', args=['zsh', '-c', 'exit'])

    assert cat.is_handled
    assert sleep.is_handled
    assert bash.is_handled
    assert not zsh.is_handled
    assert empty.is_handled


def test_command_matching_setup():
    bash = Entrypoint(conf='configs/matching_command.yml', args=['bash'])
    zsh = Entrypoint(conf='configs/matching_command.yml', args=['zsh'])

    assert bash.config.user == 1000
    assert zsh.config.user == 1001

    assert bash.config.group == 1002
    assert zsh.config.group == 1003

    assert bash.config.config_files == [
        'file1.tpl',
        {'file2': 'file3'},
        'file4',
        'file9',
        {'file10': 'file11'},
    ]
    assert zsh.config.config_files == [
        'file5.tpl',
        {'file6': 'file7'},
        'file8',
        'file9',
        {'file10': 'file11'},
    ]

    assert bash.config.secret_env == [
        'secret1',
        'secret2',
    ]
    assert zsh.config.secret_env == [
        'secret1',
        'secret3',
    ]

    assert bash.config.pre_conf_commands == [
        'cmd1',
        'cmd3',
    ]
    assert zsh.config.pre_conf_commands == [
        'cmd2',
        'cmd3',
    ]

    assert bash.config.post_conf_commands == [
        'cmd4',
        'cmd6',
    ]
    assert zsh.config.post_conf_commands == [
        'cmd4',
        'cmd5',
    ]

    assert bash.config.post_run_commands == [
        'cmd7',
        'cmd8',
    ]
    assert zsh.config.post_run_commands == [
        'cmd8',
        'cmd9',
    ]

    assert bash.config.debug
    assert zsh.config.debug

    assert bash.config.clean_env
    assert not zsh.config.clean_env

    assert bash.config.remove_dockerenv
    assert zsh.config.remove_dockerenv
