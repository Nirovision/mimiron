# -*- coding: utf-8 -*-

config_schema = {
    'type': 'object',
    'properties': {
        'terraformRepositories': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'path': {
                        'type': 'string',
                    },
                    'tagEnvironment': {
                        'type': ['string', 'null'],
                    },
                    'defaultEnvironment': {
                        'type': ['string', 'null'],
                    },
                    'defaultGitBranch': {
                        'type': 'string',
                    },
                },
                'required': ['path', 'defaultGitBranch'],
            },
        },
        'dockerhub': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                },
                'password': {
                    'type': 'string',
                },
                'organization': {
                    'type': 'string',
                },
            },
            'required': ['username', 'password', 'organization'],
        },
    },
    'required': ['terraformRepositories', 'dockerhub'],
}
