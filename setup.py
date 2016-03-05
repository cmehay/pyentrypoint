#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

# Thanks Sam and Max

setup(

    name='pyentrypoint',

    version='0.1.12',

    packages=find_packages(),

    author="Christophe Mehay",

    author_email="cmehay@nospam.student.42.fr",

    description="pyentrypoint manages entrypoints in Docker containers.",

    long_description=open('README.md').read(),

    install_requires=['Jinja2>=2.8',
                      'PyYAML>=3.11',
                      'Twiggy>=0.4.7',
                      'argparse>=1.4.0',
                      'six>=1.10.0'],

    include_package_data=True,

    url='http://github.com/cmehay/pyentrypoint',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: System :: Installation/Setup",
    ],


    entry_points={
        'console_scripts': [
            'pyentrypoint = pyentrypoint.__main__:main',
        ],
    },

    license="WTFPL",

)
