# -*- coding: utf-8 -*-
from . import Command as _Command
from ...vendor import git_extensions


class History(_Command):
    def _validate_and_configure(self):
        super(self.__class__, self)._validate_and_configure()
        self.deployment_repo = self.config['TF_DEPLOYMENT_REPO']

    def _group_commits_by_author(self):
        data = {}
        for commit in self.deployment_repo.iter_commits():
            pass
        return data

    def _run(self):
        git_extensions.sync_updates(self.deployment_repo)
        commits = self._group_commits_by_author()
