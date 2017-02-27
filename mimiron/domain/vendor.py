# -*- coding: utf-8 -*-
from . import BaseMimironException
from git import InvalidGitRepositoryError as _InvalidGitRepositoryError


# PyGit custom exceptions


class InvalidGitRepo(BaseMimironException, _InvalidGitRepositoryError):
    def __init__(self, path):
        super(self.__class__, self).__init__('"%s" is an invalid git repository ' % path)


class FetchRemoteUnknownNextStep(BaseMimironException):
    pass


class UnexpectedGitError(BaseMimironException):
    pass


class NoChangesEmptyCommit(BaseMimironException):
    pass


class SyncRemoteError(BaseMimironException):
    pass


# Terraform variables custom exceptions


class TFVarsMissingConfigFile(BaseMimironException):
    def __init__(self, path):
        message = 'cannot find terraform tfvars config "%s"' % path
        super(self.__class__, self).__init__(message)


class TFVArsConfigNeverLoaded(BaseMimironException):
    def __init__(self):
        message = 'tfvars config was never loaded'
        super(self.__class__, self).__init__(message)


class InvalidTFVarsConfig(BaseMimironException):
    def __init__(self, path, error):
        message = 'error found in tfvars config "%s"\n %s' % (path, error)
        super(self.__class__, self).__init__(message)


# DockerHub custom exceptions


class InvalidDockerHubCredentials(BaseMimironException):
    def __init__(self):
        message = 'failed to authenticate against dockerhub'
        super(self.__class__, self).__init__(message)


class DockerConnectionError(BaseMimironException):
    def __init__(self):
        message = 'failed to connect to dockerhub auth servers'
        super(self.__class__, self).__init__(message)
