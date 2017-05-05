# -*- coding: utf-8 -*-
from functools import wraps

from git.exc import GitCommandError
from ...domain.vendor import UnexpectedGitError


def git_failure(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GitCommandError as e:
            raise UnexpectedGitError(e)
    return wrapper
