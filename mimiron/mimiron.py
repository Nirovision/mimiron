#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mimiron.py

usage:
  mim

options:
  -h --help     shows this
  -v --version  shows version
"""
from __future__ import print_function

from . import __version__
from docopt import docopt

import config
from .core.io import err
from .domain import BaseMimironException


def _parse_user_input(args):
    print(args)


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
