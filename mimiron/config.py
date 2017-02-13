# -*- coding: utf-8 -*-
import os

from git import Repo
from git import InvalidGitRepositoryError as _InvalidGitRepositoryError

from .domain.config import DeploymentRepoNotFound, TFVarsRepoNotFound
from .domain.config import MissingDockerCredentials, MissingDockerOrg
from .domain.config import EditorNotSpecified
from .domain.config import InvalidRepositoryPath
from .domain.vendor import InvalidGitRepo

config = {
    'TF_DEPLOYMENT_PATH': os.environ.get('TF_DEPLOYMENT_PATH'),
    'TF_DEPLOYMENT_REPO': None,
    'TF_VARS_STAGING_PATH': os.environ.get('TF_VARS_STAGING_PATH'),
    'TF_VARS_STAGING_REPO': None,
    'TF_VARS_PRODUCTION_PATH': os.environ.get('TF_VARS_PRODUCTION_PATH'),
    'TF_VARS_PRODUCTION_REPO': None,
    'DOCKER_USERNAME': os.environ.get('DOCKER_USERNAME'),
    'DOCKER_PASSWORD': os.environ.get('DOCKER_PASSWORD'),
    'DOCKER_ORG': os.environ.get('DOCKER_ORG'),
    'EDITOR': os.environ.get('EDITOR', 'vi'),
}


def validate():
    if not config['TF_DEPLOYMENT_PATH']:
        raise DeploymentRepoNotFound
    if not config['TF_VARS_STAGING_PATH']:
        raise TFVarsRepoNotFound('staging')

    if not config['DOCKER_USERNAME']:
        raise MissingDockerCredentials('username')
    if not config['DOCKER_PASSWORD']:
        raise MissingDockerCredentials('password')
    if not config['DOCKER_ORG']:
        raise MissingDockerOrg()

    if not config['EDITOR']:
        raise EditorNotSpecified()
    return None


def post_process():
    map(_build_repo_from_paths, [
        ('TF_DEPLOYMENT_PATH', 'TF_DEPLOYMENT_REPO',),
        ('TF_VARS_STAGING_PATH', 'TF_VARS_STAGING_REPO',),
        ('TF_VARS_PRODUCTION_PATH', 'TF_VARS_PRODUCTION_REPO',),
    ])


def _build_repo_from_paths(keys):
    key, repo_key = keys
    if config[key] is None:
        return None

    path = os.path.expanduser(config[key])
    if not os.path.isdir(path):
        raise InvalidRepositoryPath(path)
    try:
        repo = Repo(path)
        if repo.bare:
            raise _InvalidGitRepositoryError
        config[repo_key] = repo
    except _InvalidGitRepositoryError:
        raise InvalidGitRepo(path)
    return None
