# -*- coding: utf-8 -*-
import json
import os

from jsonschema import validate as validate_schema
from jsonschema.exceptions import ValidationError

from git import Repo
from git import InvalidGitRepositoryError as _InvalidGitRepositoryError
from git import NoSuchPathError as _NoSuchPathError

from ..schemas.config import config_schema
from ..domain.config import ConfigLoadError, MalformedConfig
from ..domain.config import DeploymentRepositoriesNotSpecified
from ..domain.vendor import InvalidGitRepository

__all__ = ['Config']


class Config(object):
    def __init__(self, config=None, config_path='~/.mimiron.json'):
        self.data = config or {}
        self._config_path = os.path.expanduser(config_path)

    def init(self):
        self.read()
        self.validate()
        self.process()

    def read(self, force=False):
        """Reads base configuration file defined by `config_path`."""
        if self.data and not force:
            return None
        try:
            with open(self._config_path, 'rU') as f:
                self.data = json.loads(f.read())
        except IOError:
            raise ConfigLoadError(self._config_path)
        return None

    def validate(self):
        """Validates the base configuration file is correct against the `config_schema`."""
        try:
            validate_schema(self.data, config_schema)
        except ValidationError as e:
            raise MalformedConfig(e.message)

    def process(self):
        """Initialises Mimiron using the configuration found in `config_path`."""
        for i, repo in enumerate(self.data['terraformRepositories']):
            path = os.path.expanduser(repo['path'])
            try:
                git_repo = Repo(path)
                if git_repo.bare:
                    raise _InvalidGitRepositoryError
                repo['git'] = git_repo
                repo['defaultEnvironment'] = repo.get('defaultEnvironment', None)
            except _InvalidGitRepositoryError:
                raise InvalidGitRepository(path)
            except _NoSuchPathError:
                raise DeploymentRepositoriesNotSpecified
