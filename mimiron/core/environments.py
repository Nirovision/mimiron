# -*- coding: utf-8 -*-
STAGING = 'staging'
PRODUCTION = 'production'


def is_valid_env(env):
    return env.lower() in [PRODUCTION, STAGING]  # only 2 for now.
