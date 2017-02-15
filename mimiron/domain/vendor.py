# -*- coding: utf-8 -*-
from . import BaseMimironException
from git import InvalidGitRepositoryError as _InvalidGitRepositoryError


class InvalidGitRepo(BaseMimironException, _InvalidGitRepositoryError):
    def __init__(self, path):
        super(self.__class__, self).__init__('"%s" is an invalid git repository ' % path)


class FetchRemoteUnknownNextStep(BaseMimironException):
    pass


class UnexpectedGitError(BaseMimironException):
    pass


class NoChangesEmptyCommit(BaseMimironException):
    pass


class TFVarsMissingConfigFile(BaseMimironException):
    def __init__(self, path):
        message = 'cannot find terraform tfvars config "%s"' % path
        super(self.__class__, self).__init__(message)


class InvalidTFVarsConfig(BaseMimironException):
    def __init__(self, path, error):
        message = 'error found in tfvars config "%s"\n %s' % (path, error)
        super(self.__class__, self).__init__(message)
