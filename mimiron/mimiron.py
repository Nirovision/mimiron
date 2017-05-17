#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
    mim (bump|b) <service> [--env=<env>] [--latest] [--no-push] [--show-all]
    mim (status|st) [--env=<env>]
    mim (deploy|d) [--show-last=<n>] [--env=<env>] [--no-push]

commands:
    (bump|b)         bumps the <service> with an image <artifact>
    (status|st)      shows the currently used artifact id for <env>
    (deploy|d)       triggers a deploy for an environment --env=<env>

arguments:
    <artifact>       the deployment artifact we are pushing (e.g. Docker image/AMI)
    <service>        the application we're targeting
    --env=<env>      the environment we want to change [default: %s]
    --show-all       show all artifacts for the current service
    --show-last=<n>  show the last n commits [default: %s]

options:
    --no-push        make local changes without pushing to remote
    --latest         use the latest artifact when updating a service

    -h --help        shows this
    -v --version     shows version
"""
from __future__ import print_function

from . import __version__
from docopt import docopt

import config
from .core import io
from .core.commands import bump
from .core.commands import status
from .core.commands import deploy

from .domain import BaseMimironException
from .domain.commands import UnexpectedCommand

from .core import constants as const


def _parse_user_input(args):
    env = args['--env'].lower()
    if env == const.PRODUCTION:
        io.warn('!!!beware!!! you are operating inside --env="%s" environment!' % env)

    if any([args['bump'], args['b']]):
        return bump.Bump(
            env=env,
            service=args['<service>'],
            is_latest=args['--latest'],
            is_show_all=args['--show-all'],
            should_push=not args['--no-push']
        )
    if any([args['status'], args['st']]):
        return status.Status(env=env)
    if any([args['deploy'], args['d']]):
        return deploy.Deploy(
            env=env,
            show_last_limit=args['--show-last'],
            should_push=not args['--no-push']
        )
    raise UnexpectedCommand


def main():
    try:
        definition = __doc__ % (
            config.config['DEFAULT_ENVIRONMENT'],
            config.config['DEFAULT_SHOW_LAST_LIMIT']
        )
        args = docopt(definition, version=__version__)

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
