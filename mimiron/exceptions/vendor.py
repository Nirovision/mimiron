# -*- coding: utf-8 -*-
from . import BaseMimironException
from git import InvalidGitRepositoryError as _InvalidGitRepositoryError


# PyGit custom exceptions


class InvalidGitRepository(BaseMimironException, _InvalidGitRepositoryError):
    def __init__(self, path):
        super(InvalidGitRepository, self).__init__('"%s" is an invalid git repository ' % (path,))


class FetchRemoteUnknownNextStep(BaseMimironException):
    pass


class UnexpectedGitError(BaseMimironException):
    pass


class NoChangesEmptyCommit(BaseMimironException):
    pass


class SyncRemoteError(BaseMimironException):
    pass


# Terraform variables custom exceptions


class NoTFVarsFilesFound(BaseMimironException):
    def __init__(self, path):
        message = 'there are no terraform tfvar files found in "%s"' % (path,)
        super(NoTFVarsFilesFound, self).__init__(message)


class TFVarsMissingConfigFile(BaseMimironException):
    def __init__(self, path):
        message = 'cannot find terraform tfvars config "%s"' % (path,)
        super(TFVarsMissingConfigFile, self).__init__(message)


class TFVarsDuplicateKeys(BaseMimironException):
    def __init__(self, key, path):
        message = 'duplicate keys found between tfvars: "%s" in "%s"' % (key, path,)
        super(TFVarsDuplicateKeys, self).__init__(message)


class InvalidTFVarsConfig(BaseMimironException):
    def __init__(self, path, error):
        message = 'error found in tfvars config "%s"\n %s' % (path, error,)
        super(InvalidTFVarsConfig, self).__init__(message)


# DockerHub custom exceptions


class InvalidDockerHubCredentials(BaseMimironException):
    def __init__(self):
        message = 'failed to authenticate against dockerhub'
        super(InvalidDockerHubCredentials, self).__init__(message)


class DockerConnectionError(BaseMimironException):
    def __init__(self):
        message = 'failed to connect to dockerhub auth servers'
        super(DockerConnectionError, self).__init__(message)
