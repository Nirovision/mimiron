#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
    mim bump <service> <env> [--latest] [--no-push]
    mim status <env>

commands:
    bump          bumps the <service> with an image <artifact>
    status        shows the currently used artifact id for <env>

arguments:
    <artifact>    the deployment artifact we are pushing (e.g. Docker image/AMI)
    <service>     the application we're targeting
    <env>         the environment we want to change

options:
    --no-push     make local changes without pushing to remote
    --latest      use the latest artifact when updating a service

    -h --help     shows this
    -v --version  shows version
"""
from __future__ import print_function

from . import __version__
from docopt import docopt

import config
from .core import io
from .core.commands import bump
from .core.commands import status

from .domain import BaseMimironException
from .domain.commands import UnexpectedCommand


def _parse_user_input(args):
    env = args['<env>']

    if args['bump']:
        return bump.Bump(
            env=env,
            service=args['<service>'],
            is_latest=args['--latest'],
            should_push=not args['--no-push']
        )
    if args['status']:
        return status.Status(env=env)
    raise UnexpectedCommand


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
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
