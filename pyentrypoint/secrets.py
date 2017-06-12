"""
    Get secrets in containers
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os


class Secrets(object):
    "Secret loader"

    secret_dir = '/run/secrets'
    secret_files = ()

    def __init__(self):
        self._idx = 0
        if os.path.exists(self.secret_dir):
            self.secret_files = os.listdir(self.secret_dir)

    def __len__(self):
        return len(self.secret_files)

    def __getitem__(self, key):
        if key not in self.secret_files:
            raise KeyError
        return self._read_file(key)

    def __iter__(self):
        return self

    def __next__(self):
        idx = self._idx
        self._idx += 1
        try:
            self.secret_files[idx]
        except IndexError:
            raise StopIteration
        return self._read_file(file=self.secret_files[idx])

    def _read_file(self, file):
        with open(os.path.join(self.secret_dir, file), 'r') as s:
            return s.read()
