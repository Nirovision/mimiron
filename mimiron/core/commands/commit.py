# -*- coding: utf-8 -*-
from . import Command as _Command

from ..environments import is_valid_env
from ..environments import get_env_repo

from ...vendor import git_extensions as git
from ...domain.commands import InvalidEnvironment


class Commit(_Command):
    def _validate_and_configure(self):
        env = self.kwargs['env']
        if not is_valid_env(env):
            raise InvalidEnvironment(env)

        self.env = env
        self.repo = get_env_repo(self.env)

        return True

    def _run(self):
        has_changes = git.sync_updates(self.repo)
        if has_changes:
            git.commit_and_push(self.repo)
        return True
