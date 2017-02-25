# -*- coding: utf-8 -*-
import os

from ...config import config
from ..environments import is_valid_env
from ...domain.commands import InvalidEnvironment


class Command(object):
    def __init__(self, conf=config, **kwargs):
        self.kwargs = kwargs
        self.config = conf

        self._validate_and_configure()
        self._before_run()
        self._run()
        self._after_run()

    def _validate_and_configure(self):
        env = self.kwargs.get('env')
        if env is not None and not is_valid_env(env):
            raise InvalidEnvironment(env)

        self.env = env
        self.tfvars_path = os.path.join(
            self.config['TF_DEPLOYMENT_PATH'], 'terraform/tfvars/%s.json' % self.env
        )
        self.tfvars_path = os.path.expanduser(self.tfvars_path)

    def _run(self):
        raise NotImplementedError

    def _before_run(self):
        pass

    def _after_run(self):
        pass
