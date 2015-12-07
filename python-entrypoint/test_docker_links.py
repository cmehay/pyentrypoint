# Tests using pytest

from docker_links import DockerLinks
from entrypoint import Entrypoint

LINKS = [
    'test1',
    'test2',
    'test3',
    'test4',
]


def test_all_links():
    links = DockerLinks()
    all_links = links.links()
    print(links.to_json())

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


def test_entrypoint():
    entry = Entrypoint()

    print(vars(entry.config))

    print('all')
    for link in entry.config.links.all:
        print(vars(link))
    print('test1')
    for link in entry.config.links.test1:
        print(vars(link))
    print('test2_800')
    for link in entry.config.links.test2_800:
        print(vars(link))
    print('test1')
    for link in entry.config.links.test2:
        print(vars(link))
