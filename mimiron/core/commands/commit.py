# -*- coding: utf-8 -*-
from . import Command as _Command
from ...vendor import git_extensions as git


class Commit(_Command):
    def _run(self):
        has_changes = git.sync_updates(self.repo)
        if has_changes:
            git.commit_and_push(self.repo)
        return True
