# -*- coding: utf-8 -*-
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
