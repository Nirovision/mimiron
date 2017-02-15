# -*- coding: utf-8 -*-
import json

from ..domain.vendor import TFVarsMissingConfigFile
from ..domain.vendor import InvalidTFVarsConfig


def validate_tfvars(path):
    try:
        with open(path, 'rU') as f:
            json.load(f)
    except IOError:
        raise TFVarsMissingConfigFile(path)
    except (TypeError, ValueError) as e:
        raise InvalidTFVarsConfig(path, e)
