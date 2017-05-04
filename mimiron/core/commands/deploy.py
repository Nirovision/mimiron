# -*- coding: utf-8 -*-
from . import Command as _Command
from ...vendor import git_extensions


class Deploy(_Command):
    def _validate_and_configure(self):
        super(self.__class__, self)._validate_and_configure()
        self.deployment_repo = self.config['TF_DEPLOYMENT_REPO']

    def _run(self):
        git_extensions.sync_updates(self.deployment_repo)
