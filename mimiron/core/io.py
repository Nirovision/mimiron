# -*- coding: utf-8 -*-
from __future__ import print_function
import sys


def err(message, exit_=True):
    print('[error] %s' % message, file=sys.stderr)
    if exit_:
        exit(1)


def warn(message):
    print('[warn] %s' % message, file=sys.stderr)


def info(message, end='\n'):
    print('[info] %s' % message, file=sys.stdout, end=end)


def ok(message):
    print('[ok] %s' % message, file=sys.stdout)
