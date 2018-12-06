'''Helper functions for resolving and dealing with env'''
from typing import Optional
import sys
import os

VALID_ENVS = {'test', 'stag', 'prod'}


def get_env() -> str:
    '''Get env variable from either arguments or environmental variables'''
    env = get_env_from_args()
    if env is None:
        env = get_env_from_vars()
    if env is None:
        raise ValueError('Could not resolve environment!')
    if not is_valid_env(env):
        raise ValueError(f'Resolved environment {env} is not valid!')
    return env

def get_env_from_args() -> Optional[str]:
    '''Get env variable from args (-e or --env)'''
    args = sys.argv
    if '-e' in args:
        return args[args.index('-e') + 1]
    if '--env' in args:
        return args[args.index('--env') + 1]
    for arg in args:
        if is_valid_env(arg):
            return arg
    return None

def get_env_from_vars() -> Optional[str]:
    '''Get env variable from environmental variables (ENVIRONMENT or ENV)'''
    env = os.getenv('ENVIRONMENT')
    if env is not None:
        return env
    return os.getenv('ENV')

def is_valid_env(env) -> bool:
    '''Check whether environment is valid'''
    return env in VALID_ENVS
