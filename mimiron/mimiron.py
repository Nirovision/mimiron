#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
  mim fast-deploy [<artifact>|<service>] [<environment>]
  mim deploy <environment> [--no-push]
  mim commit <environment>

commands:
  fast-deploy    update ami/sha and auto-deploy after update
  deploy         updates the tfvars commit sha in deployments
  commit         generates a commit message based on changes found

arguments:
  <artifact>     the deployment artifact we are pushing (e.g. Docker image/AMI)
  <service>      the application/microservice we're targeting
  <environment>  the environment we want to change

options:
  --no-push      make local changes without pushing to remote

  -h --help      shows this
  -v --version   shows version
"""
from __future__ import print_function

from . import __version__
from docopt import docopt

import config
from .core.commands import commit, deploy, fast_deploy
from .core.io import err
from .domain import BaseMimironException


def _parse_user_input(args):
    env = args['<environment>']

    if args['fast-deploy']:
        return fast_deploy.FastDeploy(
            environment=env,
            artifact=args['<artifact>'],
            service=args['<service>']
        )
    if args['deploy']:
        should_push = not args['--no-push']
        return deploy.Deploy(environment=env, should_push=should_push)
    if args['commit']:
        return commit.Commit(environment=env)
    err('encountered unexpected mim command')


def main():
    args = docopt(__doc__, version=__version__)
    try:
        config.validate()
        _parse_user_input(args)
    except KeyboardInterrupt:
        pass
    except BaseMimironException as e:
        err(e)
    exit(0)


if __name__ == '__main__':
    main()
