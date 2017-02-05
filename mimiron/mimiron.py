#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
  mim fast-deploy [<artifact>|<service>] [<env>]
  mim deploy <env> [--no-push]
  mim commit <env>

commands:
  fast-deploy   update ami/sha and auto-deploy after update
  deploy        updates the tfvars commit sha in deployments
  commit        generates a commit message based on changes found

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
from .core.commands import commit, deploy, fast_deploy
from .domain import BaseMimironException


def _parse_user_input(args):
    env = args['<env>']

    if args['fast-deploy']:
        return fast_deploy.FastDeploy(
            env=env,
            artifact=args['<artifact>'],
            service=args['<service>']
        )
    if args['deploy']:
        should_push = not args['--no-push']
        return deploy.Deploy(env=env, should_push=should_push)
    if args['commit']:
        return commit.Commit(env=env)
    io.err('encountered unexpected mim command')


def main():
    args = docopt(__doc__, version=__version__)
    try:
        config.validate()
        _parse_user_input(args)
    except KeyboardInterrupt:
        pass
    except BaseMimironException as e:
        io.err(e)
    exit(0)


if __name__ == '__main__':
    main()
