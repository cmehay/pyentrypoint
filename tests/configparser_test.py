from commons import clean_env

from pyentrypoint.configparser import ConfigParser


def teardown_function(function):
    clean_env()


def test_configparser():
    config = '''
[ini]
content = ok
    '''.strip()

    c = ConfigParser()
    c.read_string(config)

    assert str(c).strip() == config
