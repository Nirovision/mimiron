# -*- coding: utf-8 -*-
from ...config import config

from ..environments import is_valid_env
from ..environments import get_env_repo

from ...domain.commands import InvalidEnvironment
from ...domain.commands import EnvironmentNotLinked


class Command(object):
    def __init__(self, conf=config, **kwargs):
        self.kwargs = kwargs
        self.config = conf

        self._validate_and_configure()
        self._run()

    def _validate_and_configure(self):
        env = self.kwargs.get('env')
        if env is not None and not is_valid_env(env):
            raise InvalidEnvironment(env)

        self.env = env
        self.repo = get_env_repo(self.env)
        if self.env and not self.repo:
            raise EnvironmentNotLinked(env)

    def _run(self):
        raise NotImplementedError
