# -*- coding: utf-8 -*-
import json
import copy

from ..domain.vendor import TFVarsMissingConfigFile
from ..domain.vendor import InvalidTFVarsConfig
from ..domain.vendor import TFVArsConfigNeverLoaded


class TFVarsConfig(object):
    SUPPORTED_TYPES = {
        'docker': 'DOCKER_IMAGE',
        'ami': 'AMI',
    }

    def __init__(self, tfvars_path):
        self.tfvars_path = tfvars_path

        self.config = {}
        self.has_loaded_config = False

    def load(self):
        try:
            with open(self.tfvars_path, 'rU') as f:
                self.config = json.load(f)
        except IOError:
            raise TFVarsMissingConfigFile(self.tfvars_path)
        except (TypeError, ValueError) as e:
            raise InvalidTFVarsConfig(self.tfvars_path, e)

        self.has_loaded_config = True
        return copy.deepcopy(self.config)

    def save(self):
        if not self.has_loaded_config:
            raise TFVArsConfigNeverLoaded
        try:
            with open(self.tfvars_path, 'w') as f:
                data = json.dumps(self.config, f, ensure_ascii=False, indent=2, sort_keys=True)
                data = data.split('\n')
                data = [d.rstrip() for d in data]
                data = '\n'.join(data)
                f.write(data)
        except IOError:
            raise TFVarsMissingConfigFile(self.tfvars_path)

    def normalize_service_name(self, service):
        return str(service).strip().replace('-', '_')

    def update_var(self, name, value):
        self.config[name] = value

    def get_var(self, name):
        return self.config[name]


def load_tfvars(path):
    try:
        with open(path, 'rU') as f:
            return json.load(f)
    except IOError:
        raise TFVarsMissingConfigFile(path)
    except (TypeError, ValueError) as e:
        raise InvalidTFVarsConfig(path, e)


def normalize_service_name(service):
    return str(service).strip().replace('-', '_')
