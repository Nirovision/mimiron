#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from mimiron import __version__

setup(
    name='mimiron',
    version=__version__,
    description="Mimiron is a CLI tool whose purpose is to provide a better workflow when manging tfvars",
    url='https://github.com/ImageIntelligence/mimiron',

    author='David Vuong',
    author_email='david@imageintelligence.com',

    classifiers=[
        'Intended Audience :: Developers',

        'Environment :: Console',

        'Topic :: Utilities',

        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=[
        'docopt==0.6.2',
        'terminaltables==3.1.0',
        'GitPython==2.1.1',
        'requests==2.13.0',
        'humanize==0.5.1',
        'python-dateutil==2.6.0',
    ],
    include_package_data=True,
    package_data={'': ['README.md']},

    entry_points={
        'console_scripts': [
            'mim=mimiron.mimiron:main',
        ],
    },
)
