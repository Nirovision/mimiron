# -*- coding: utf-8 -*-
from . import BaseMimironException


class InvalidEnvironment(BaseMimironException):
    def __init__(self, env):
        message = '"%s" environment is invalid' % env
        super(self.__class__, self).__init__(message)


class EnvironmentNotLinked(BaseMimironException):
    def __init__(self, env):
        message = '"%s" environment is not linked (ref `env`)' % env
        super(self.__class__, self).__init__(message)
