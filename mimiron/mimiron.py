#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
    mim (bump|b) <service> [--env=<env>] [-t] [--no-push] [--show-all]
    mim (status|st) [--env=<env>]
    mim (deploy|d) [--show-last=<n>] [--no-push] [-t] [--empty-commit]

commands:
    (bump|b)         bumps the <service> with an image <artifact>
    (status|st)      shows the currently used artifact id for <env>
    (deploy|d)       triggers a deploy a chosen deployment repository

arguments:
    <artifact>       the deployment artifact (Docker image) we are pushing
    <service>        the application we're targeting
    --env=<env>      overrides the default repo environment
    --show-all       show all artifacts for the current service
    --show-last=<n>  show the last n commits
    --empty-commit   creates an empty commit on the chosen repository
    -t --tag         creates a git tag (git tag -a) on a chosen commit or [--empty-commit]

options:
    --no-push        make local changes without pushing to remote
    --latest         use the latest artifact when updating a service

    -h --help        shows this
    -v --version     shows version
"""
from __future__ import print_function

from . import __version__
from docopt import docopt

from .core import io
from .core.commands import bump
from .core.commands import status
from .core.commands import deploy
from .core.config import Config

from .exceptions import BaseMimironException
from .exceptions.commands import UnexpectedCommand


def _parse_user_input(args, config):
    if any([args['bump'], args['b']]):
        return bump.Bump(
            config,
            env=args['--env'],
            tag=args['--tag'],
            service=args['<service>'],
            is_show_all=args['--show-all'],
            should_push=not args['--no-push']
        )
    if any([args['status'], args['st']]):
        return status.Status(config, env=args['--env'])
    if any([args['deploy'], args['d']]):
        return deploy.Deploy(
            config,
            is_tag=args['--tag'],
            is_empty_commit=args['--empty-commit'],
            show_last_limit=args['--show-last'],
            should_push=not args['--no-push']
        )
    raise UnexpectedCommand


def main():
    try:
        args = docopt(__doc__, version=__version__)

        config = Config()
        config.init()

        _parse_user_input(args, config)
    except KeyboardInterrupt:
        pass
    except BaseMimironException as e:
        io.err(e)
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
