# -*- coding: utf-8 -*-
from . import BaseMimironException


class DeploymentRepoNotFound(BaseMimironException):
    def __init__(self):
        message = 'deployment repository not found'
        super(self.__class__, self).__init__(message)


class TFVarsRepoNotFound(BaseMimironException):
    def __init__(self, env):
        message = '"%s" environment repository not specified' % env
        super(self.__class__, self).__init__(message)


class MissingDockerCredentials(BaseMimironException):
    def __init__(self, missing_credential):
        message = 'missing docker credentials "%s"' % missing_credential
        super(self.__class__, self).__init__(message)


class InvalidRepositoryPath(BaseMimironException):
    def __init__(self, path):
        super(self.__class__, self).__init__('"%s" directory does not exist' % path)
