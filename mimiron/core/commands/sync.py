# -*- coding: utf-8 -*-
from . import Command as _Command
from ...vendor import git_extensions as git
from .. import io


class Sync(_Command):
    def _run(self):
        for repo in [
            self.config['TF_DEPLOYMENT_REPO'],
            self.config['TF_VARS_STAGING_REPO'],
            self.config['TF_VARS_PRODUCTION_REPO'],
        ]:
            if repo is None:
                continue
            git.sync_updates(repo, push=True)
            git.sync_submodule_updates(repo)
        io.ok('repository sync complete')
        return None
