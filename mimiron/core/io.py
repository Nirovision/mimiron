#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import sys

from terminaltables import SingleTable

# @see: http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html
U_ERROR = '\033[1;31mERR ✖\033[0m'
U_WARNING = '\033[33m[warn]\033[0m'
U_INFO = '\033[34m==>\033[0m'
U_OK = '\033[32mOK ✓\033[0m'


def _to_utf8(message):
    try:
        return message.encode('utf-8')
    except UnicodeDecodeError:
        return message


def _print_message(stream, *components):
    message = ' '.join(map(unicode, components))
    return print(message, file=stream)


def err(message, exit_=False):
    _print_message(sys.stderr, U_ERROR, message)
    if exit_:
        exit(0)


def warn(message):
    _print_message(sys.stderr, U_WARNING, message)


def info(message):
    _print_message(sys.stdout, U_INFO, message)


def ok(message):
    _print_message(sys.stdout, U_OK, message)


def print_table(rows, title):
    print(SingleTable(rows, title).table)


def collect_input(prompt, selection):
    """Prompts the user to select an option in the `selection` list."""
    message = _to_utf8('%s %s ' % (U_INFO, prompt))
    while True:
        id_ = raw_input(message)
        if id_ == 'q':
            return None
        try:
            id_ = int(id_) - 1
            if id_ < 0:
                continue
            return selection[id_]
        except (ValueError, IndexError):
            continue
    return None
