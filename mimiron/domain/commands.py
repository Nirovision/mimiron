# -*- coding: utf-8 -*-
from . import BaseMimironException


class InvalidEnvironment(BaseMimironException):
    def __init__(self, env):
        message = '"%s" environment is invalid' % env
        super(self.__class__, self).__init__(message)


class UnexpectedCommand(BaseMimironException):
    def __init__(self):
        message = 'encountered unexpected command, input parser error'
        super(self.__class__, self).__init__(message)
