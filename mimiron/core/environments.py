# -*- coding: utf-8 -*-
import os
from ..config import config

STAGING = 'staging'
PRODUCTION = 'production'


def is_valid_env(env):
    return env.lower() in [PRODUCTION, STAGING]  # only 2 for now.


def get_env_repo(env):
    if env == PRODUCTION:
        return config['TF_VARS_PRODUCTION_REPO']
    if env == STAGING:
        return config['TF_VARS_STAGING_REPO']
    return None


def get_env_repo_name(env):
    repo_name = None
    if env == PRODUCTION:
        repo_name = config['TF_VARS_PRODUCTION_PATH']
    if env == STAGING:
        repo_name = config['TF_VARS_STAGING_PATH']
    return os.path.split(repo_name)[-1] if repo_name else repo_name
