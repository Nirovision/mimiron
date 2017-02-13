#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
    mim deploy <service> <env> [<artifact>]
    mim set-sha <env> [--no-push]
    mim set-var <env>
    mim sync
    mim edit <env>

commands:
    deploy        update ami/sha and auto-deploy after update
    set-sha       update tfvars commit sha in deployments and push to remote
    set-var       commit and pushes tfvars for <env> based on changes found
    sync          calls git fetch on all associated git repos
    edit          opens the tfvar config in the default editor

arguments:
    <artifact>    the deployment artifact we are pushing (e.g. Docker image/AMI)
    <service>     the application/microservice we're targeting
    <env>         the environment we want to change

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
from .core.commands import deploy, sync, edit
from .core.commands import set_sha, set_var
from .domain import BaseMimironException


def _parse_user_input(args):
    env = args['<env>']

    if args['deploy']:
        return deploy.Deploy(
            env=env, service=args['<service>'], artifact=args['<artifact>']
        )
    if args['set-sha']:
        should_push = not args['--no-push']
        return set_sha.SetSha(env=env, should_push=should_push)
    if args['set-var']:
        return set_var.SetVar(env=env)
    if args['sync']:
        return sync.Sync()
    if args['edit']:
        return edit.Edit(env=env)
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
