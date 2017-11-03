# -*- coding: utf-8 -*-
import os
import json
from collections import defaultdict

from ..exceptions.vendor import TFVarsMissingConfigFile
from ..exceptions.vendor import InvalidTFVarsConfig
from ..exceptions.vendor import TFVarsDuplicateKeys

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
        duplicates = defaultdict(lambda: defaultdict(bool))
        for tfvars in self.data.itervalues():
            for k in tfvars['data'].iterkeys():
                if duplicates[tfvars['group']].get(k):
                    raise TFVarsDuplicateKeys(k, self.repo['path'])
                duplicates[tfvars['group']][k] = True
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

    def get_services(self, group):
        """Retrieves all services found based on tfvar files found in `self.data`.

        `self.data` is a dictionary in the form:

        >>> data = {
        ...    'path_1': {
        ...        'path': 'path_1',
        ...        'group': 'xxx',
        ...        'data': {
        ...            'service_1_image': 'xxx',
        ...            'service_1_attr_1': 'yyy',
        ...            'service_1_attr_2': 'zzz',
        ...            'service_2_image': 'xxx',
        ...            'service_3_image': 'xxx',
        ...        },
        ...    },
        ...    'path_2': {
        ...        'path': 'path_2',
        ...        'group': 'xxx',
        ...        'data': {
        ...            'service_4_image': 'xxx',
        ...            'service_4_attr_1': 'yyy',
        ...            'service_4_attr_2': 'zzz',
        ...            'service_5_image': 'xxx',
        ...        },
        ...    },
        ... }

        The result from all of this, should look like:

        >>> result = {
        ...     'service_1': {
        ...         'image': 'xxx',
        ...         'attr_1': 'yyy',
        ...         'attr_2': 'zzz',
        ...     },
        ...     'service_2': {
        ...         'image': 'xxx',
        ...     },
        ...     'service_3': {
        ...         'image': 'xxx',
        ...     },
        ...     'service_4': {
        ...         'image': 'xxx',
        ...         'attr_1': 'yyy',
        ...         'attr_2': 'zzz',
        ...     },
        ...     'service_5': {
        ...         'image': 'xxx',
        ...     },
        ... }

        """
        services = defaultdict(dict)
        service_names = self.get_service_names()

        for service_name in service_names:
            for tfvars in self.data.itervalues():
                if tfvars['group'] and tfvars['group'] != group:
                    continue
                for k, v in tfvars['data'].iteritems():
                    if k.startswith(service_name):
                        services[service_name][k.replace(service_name + '_', '')] = v

        # Clean up any services that don't have any data (due to mismatched groups).
        return {k: v for k, v in services.iteritems() if v}

    def get_service_names(self):
        service_names = []
        for tfvars in self.data.itervalues():
            for k in tfvars['data'].iterkeys():
                if k.endswith('_image'):
                    service_names.append(k.replace('_image', ''))
        return service_names

    def find(self, key, group):
        for path, tfvars in self.data.iteritems():
            if group is not None and group != tfvars['group']:
                continue
            if key in tfvars['data']:
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
            if service_name in repo['tfvars'].get_service_names():
                return repo
        return None
