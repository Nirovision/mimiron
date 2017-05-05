# -*- coding: utf-8 -*-
from . import Command as _Command
from ...vendor.git_extensions import extensions as git_ext


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
        git_ext.sync_updates(self.deployment_repo)
        commits = self._group_commits_by_author()
