# -*- coding: utf-8 -*-
from . import Command as _Command
from ...vendor import git_extensions as git


class SetVar(_Command):
    def _run(self):
        has_changes = git.sync_updates(self.repo)
        if has_changes:
            message = 'chore(variables): updated variables.json config'
            git.commit_and_push(self.repo, message)
        return None
