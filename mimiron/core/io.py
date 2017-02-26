# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import sys

from terminaltables import SingleTable

# @see: http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html
U_ERROR = '\033[1;31m[error]\033[0m'
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


def err(message):
    _print_message(sys.stderr, U_ERROR, message)


def warn(message):
    _print_message(sys.stderr, U_WARNING, message)


def info(message):
    _print_message(sys.stdout, U_INFO, message)


def ok(message):
    _print_message(sys.stdout, U_OK, message)


def print_table(rows, title):
    print(SingleTable(rows, title).table)


def collect_single_input(prompt):
    message = _to_utf8('%s %s ' % (U_INFO, prompt))
    input_ = raw_input(message).strip()
    return input_ if input_ else None


def collect_input(prompt, selection):
    """Prompts the user to select an option in the `selection` list."""
    while True:
        id_ = collect_single_input(prompt)
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
