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

        self._config = {}
        self.has_loaded_config = False

    @property
    def config(self):
        return copy.deepcopy(self._config)

    def load(self):
        try:
            with open(self.tfvars_path, 'rU') as f:
                self._config = json.load(f)
        except IOError:
            raise TFVarsMissingConfigFile(self.tfvars_path)
        except (TypeError, ValueError) as e:
            raise InvalidTFVarsConfig(self.tfvars_path, e)

        self.has_loaded_config = True
        return copy.deepcopy(self._config)

    def save(self):
        if not self.has_loaded_config:
            raise TFVArsConfigNeverLoaded
        try:
            with open(self.tfvars_path, 'w') as f:
                data = json.dumps(self._config, f, ensure_ascii=False, indent=2, sort_keys=True)
                data = data.split('\n')
                data = [d.rstrip() for d in data]
                data = '\n'.join(data)
                f.write(data)
        except IOError:
            raise TFVarsMissingConfigFile(self.tfvars_path)

    def normalize_service_name(self, service):
        return str(service).strip().replace('-', '_')

    def get_artifact_key(self, service, is_ami=False):
        return service + ('_ami_id' if is_ami else '_image')

    def update_var(self, name, value):
        self._config[name] = value

    def get_var(self, name):
        return self._config[name]
