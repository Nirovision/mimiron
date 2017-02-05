# -*- coding: utf-8 -*-


def is_valid_env(env):
    return env.lower() in ['production', 'staging']  # only 2 for now.
