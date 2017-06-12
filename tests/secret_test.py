# Tests using pytest
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from yaml import load
from yaml import Loader

from pyentrypoint import Entrypoint


@pytest.mark.v3
def test_secret_templates():
    test_confs = ['configs/secret.yml']
    for test_conf in test_confs:
        entry = Entrypoint(conf='configs/secret.yml')

        conf = entry.config

        entry.apply_conf()

        for _, config_file in conf.get_templates():
            with open(config_file, mode='r') as r:
                test = load(stream=r, Loader=Loader)

            # test secrets
            assert test['SECRET']['secret1'] == 'SECRET1'
            assert test['SECRET']['secret2'] == 'SECRET2'
