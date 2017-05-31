# -*- coding: utf-8 -*-
import os

from ..constants import PRODUCTION, STAGING
from ...config import config
from ...domain.commands import InvalidEnvironment, InvalidOperatingBranch


class Command(object):
    def __init__(self, conf=config, **kwargs):
        self.kwargs = kwargs
        self.config = conf

        self.validate_and_configure()
        self._before_run()
        self.run()
        self._after_run()

    def validate_and_configure(self):
        env = self.kwargs.get('env')

        if env not in [PRODUCTION, STAGING]:  # only 2 for now.
            raise InvalidEnvironment(env)

        self.env = env
        self.tfvars_path = os.path.join(
            self.config['TF_DEPLOYMENT_PATH'], 'terraform/tfvars/%s.json' % self.env
        )
        self.tfvars_path = os.path.expanduser(self.tfvars_path)
        self.deployment_repo = self.config['TF_DEPLOYMENT_REPO']

        # All command operations can only operate within the default git branch.
        active_branch = self.deployment_repo.active_branch.name
        if active_branch != self.config['DEFAULT_GIT_BRANCH']:
            raise InvalidOperatingBranch(active_branch)

    def run(self):
        raise NotImplementedError

    def _before_run(self):
        pass

    def _after_run(self):
        pass
