from __future__ import absolute_import
from __future__ import unicode_literals

from sys import argv

from .entrypoint import main as m


def main():
    m(argv)
