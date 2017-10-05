# -*- coding: utf-8 -*-
import json
import os

from jsonschema import validate as validate_schema
from jsonschema.exceptions import ValidationError

from git import Repo
from git import InvalidGitRepositoryError as _InvalidGitRepositoryError
from git import NoSuchPathError as _NoSuchPathError

from ..schemas.config import config_schema
from ..exceptions.config import ConfigLoadError, MalformedConfig
from ..exceptions.config import DeploymentRepositoriesNotSpecified
from ..exceptions.vendor import InvalidGitRepository
from ..exceptions.vendor import NoTFVarsFilesFound

from ..vendor.terraform import TFVarsConfig

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

    def _read_tfvars(self, repo):
        """Reads all tfvars (json file) in the given `repo['path']`/terraform/tfvars directory.

        Terraform deployment projects are expected to follow this structure:

        ├── README.md
        ├── scripts
        │   └── ...
        └── terraform
            ...
            ├── main.tf
            ├── tfvars
            │   ├── variables.production.json
            │   └── variables.staging.json
            └── variables.tf

        `tfvars/` follow a flat structure. Variables are free to be split between many JSON
        files and can be grouped based on `<group>` (<name>[.<group>].json).

        NOTE: tfvar files don't need a grouping. If no group is found, the tfvar is assumed
        to be applied on all groups.

        """
        repo_path = os.path.join(repo['path'], 'terraform/tfvars')
        if not os.path.isdir(repo_path):
            raise NoTFVarsFilesFound(repo_path)

        tfvars_paths = []
        for root, dirs, files in os.walk(repo_path):
            for f in files:
                if not f.endswith('.json'):  # skip non-json files.
                    continue
                tfvars_path = os.path.join(os.path.abspath(root), f)
                tfvars_paths.append(tfvars_path)

        if not tfvars_paths:
            raise NoTFVarsFilesFound(repo_path)
        return TFVarsConfig(repo, tfvars_paths)  # aggregates all tfvars files.

    def process(self):
        """Initialises Mimiron using the configuration found in `config_path`."""
        for i, repo in enumerate(self.data['terraformRepositories']):
            repo['path'] = os.path.expanduser(repo['path'])
            try:
                git_repo = Repo(repo['path'])
                if git_repo.bare:
                    raise _InvalidGitRepositoryError
                repo['defaultEnvironment'] = repo.get('defaultEnvironment', None)
                repo['tagEnvironment'] = repo.get('tagEnvironment', None)

                repo['git'] = git_repo
                repo['tfvars'] = self._read_tfvars(repo)
            except _InvalidGitRepositoryError:
                raise InvalidGitRepository(repo['path'])
            except _NoSuchPathError:
                raise DeploymentRepositoriesNotSpecified

    def get(self, key):
        """Retrieves the `value` in `self.data` given `key`."""
        return self.data.get(key)

    def set(self, key, value):
        """Sets the `value` of item at `key` given `value`."""
        self.data[key] = value
