# -*- coding: utf-8 -*-
import os
import json

from ..domain.vendor import TFVarsMissingConfigFile
from ..domain.vendor import InvalidTFVarsConfig
from ..domain.vendor import TFVarsDuplicateKeys

__all__ = ['TFVarsConfig', 'TFVarsHelpers']


class TFVarsConfig(object):
    def __init__(self, repo, paths, load_config=True):
        self.paths = paths
        self.repo = repo
        self.data = {}

        if load_config:
            self.load()
            self.find_duplicates()

    def load(self):
        for path in self.paths:
            try:
                # NOTE: The expected file name format should be `<name>[.<group>].json`.
                _, full_filename = os.path.split(path)
                filename, _ = os.path.splitext(full_filename)
                _, group = os.path.splitext(filename)

                with open(path, 'rU') as f:
                    self.data[path] = {
                        'group': group.strip('.'),
                        'path': path,
                        'data': json.load(f),
                    }
            except IOError:
                raise TFVarsMissingConfigFile(path)
            except (TypeError, ValueError) as e:
                raise InvalidTFVarsConfig(path, e)

    def find_duplicates(self):
        """Finds duplicates between multiple tfvar config files."""
        duplicates = {}
        for tfvars in self.data.values():
            for k in tfvars['data'].keys():
                if duplicates.get(k):
                    raise TFVarsDuplicateKeys(k, self.repo['path'])
        return None

    def save(self):
        """Flushes contents in `self.data` onto disk based on the tfvar path defined as the key."""
        for path, tfvars in self.data.iteritems():
            try:
                with open(path, 'w') as f:
                    data = json.dumps(tfvars['data'], f, ensure_ascii=False, indent=2, sort_keys=True)
                    data = data.split('\n')
                    data = [d.rstrip() for d in data]
                    data = '\n'.join(data) + '\n'
                    f.write(data)
            except IOError:
                raise TFVarsMissingConfigFile(path)

    def get_services(self):
        """Retrieves all services found based on tfvar files found in `self.data`."""
        services = {}
        for tfvars in self.data.values():
            for k in tfvars['data'].iterkeys():
                if k.endswith('_image'):
                    services[k.replace('_image', '')] = {}
        for service_name, service_data in services.iteritems():
            for tfvars in self.data.values():
                for k, v in tfvars['data'].iteritems():
                    if k.startswith(service_name):
                        service_data[k.replace(service_name + '_', '')] = v
        return services

    def find(self, key, group):
        for path, tfvars in self.data.iteritems():
            if group is not None and group != tfvars['group']:
                continue
            if tfvars['data'].get(key) is not None:
                return tfvars
        return None

    def get(self, key, group):
        tfvars = self.find(key, group)
        return tfvars['data'].get(key) if tfvars else None

    def set(self, key, value, group):
        tfvars = self.find(key, group)
        if tfvars is None:
            raise NotImplementedError  # updating multiple tfvars not yet supported.
        tfvars['data'][key] = value


class TFVarsHelpers(object):
    @classmethod
    def normalize_service_name(cls, service):
        return str(service).strip().replace('-', '_')

    @classmethod
    def get_artifact_key(cls, service):
        return service + '_image'

    @classmethod
    def find_deployment_repo(cls, service, repos):
        """Given the `service` name and a list of deployment repos, determine the host repo."""
        service_name = cls.normalize_service_name(service)

        for repo in repos:
            if service_name in repo['tfvars'].get_services():
                return repo
        return None
