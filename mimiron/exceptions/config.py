# -*- coding: utf-8 -*-
from . import BaseMimironException


class ConfigLoadError(BaseMimironException):
    def __init__(self, config_path):
        message = 'failed to load configuration file: "%s"' % (config_path,)
        super(ConfigLoadError, self).__init__(message)


class MalformedConfig(BaseMimironException):
    def __init__(self, error=None):
        if error:
            message = 'malformed config file: ' + error
        else:
            message = 'malformed config file... pls fix'
        super(MalformedConfig, self).__init__(message)


class DeploymentRepositoriesNotSpecified(BaseMimironException):
    def __init__(self):
        message = 'deployment repositories not found or invalid'
        super(DeploymentRepositoriesNotSpecified, self).__init__(message)
