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
