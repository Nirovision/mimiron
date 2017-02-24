#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
    mim bump <service> <env> [<artifact>] [--ami] [--no-push]

commands:
    bump          bumps the <service> with an image <artifact>

arguments:
    <artifact>    the deployment artifact we are pushing (e.g. Docker image/AMI)
    <service>     the application we're targeting
    <env>         the environment we want to change
    --ami         signals that the service is an ami (not docker image)

options:
    --no-push     make local changes without pushing to remote

    -h --help     shows this
    -v --version  shows version
"""
from __future__ import print_function

from . import __version__
from docopt import docopt

import config
from .core import io
from .core.commands import bump
from .domain import BaseMimironException


def _parse_user_input(args):
    env = args['<env>']

    if args['bump']:
        return bump.Bump(
            env=env, service=args['<service>'], artifact=args['<artifact>']
        )
    io.err('encountered unexpected mim command')


def main():
    args = docopt(__doc__, version=__version__)
    try:
        config.validate()
        config.post_process()

        _parse_user_input(args)
    except KeyboardInterrupt:
        pass
    except BaseMimironException as e:
        io.err(e)
    exit(0)


if __name__ == '__main__':
    main()
