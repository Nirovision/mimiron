# -*- coding: utf-8 -*-
from mimiron.vendor.terraform import TFVarsConfig, TFVarsHelpers


class TestTFVarsConfig(object):
    def test_get_services_valid_config(self):
        config = TFVarsConfig(None, [], load_config=False)
        config.data = {
            '/path/repo/1': {
                'path': '/path/repo/1',
                'git': None,
                'group': 'aaa',
                'data': {
                    'my_service_1_image': 'xxx',
                    'my_service_1_desired_count': 'yyy',
                    'my_service_1_random_variable': 'zzz',

                    'my_service_2_image': 'xxx',
                    'my_service_2_desired_count': 'yyy',
                    'my_service_2_random_variable': 'zzz',
                },
            },
        }

        result = config.get_services('aaa')
        expected_output = {
            'my_service_2': {
                'image': 'xxx', 'random_variable': 'zzz', 'desired_count': 'yyy'
            },
            'my_service_1': {
                'image': 'xxx', 'random_variable': 'zzz', 'desired_count': 'yyy'
            }
        }
        assert result == expected_output

    def test_get_services_filter_group(self):
        config = TFVarsConfig(None, [], load_config=False)
        config.data = {
            '/path/repo/1': {
                'path': '/path/repo/1',
                'git': None,
                'group': 'aaa',
                'data': {
                    'my_service_1_image': 'aaa',
                    'my_service_1_desired_count': 'aaa',
                    'my_service_1_random_variable': 'aaa',
                },
            },
            '/path/repo/2': {
                'path': '/path/repo/2',
                'git': None,
                'group': 'bbb',
                'data': {
                    'my_service_1_image': 'bbb',
                    'my_service_1_desired_count': 'bbb',
                    'my_service_1_random_variable': 'bbb',
                },
            },
            '/path/repo/3': {
                'path': '/path/repo/3',
                'git': None,
                'group': 'ccc',
                'data': {
                    'my_service_2_image': 'ccc',
                    'my_service_2_desired_count': 'ccc',
                    'my_service_2_random_variable': 'ccc',
                },
            },
        }

        result = config.get_services('aaa')
        expected_output = {
            'my_service_1': {
                'image': 'aaa', 'random_variable': 'aaa', 'desired_count': 'aaa'
            }
        }
        assert result == expected_output

    def test_get_services_filter_empty_services(self):
        config = TFVarsConfig(None, [], load_config=False)
        config.data = {
            '/path/repo/1': {
                'path': '/path/repo/1',
                'git': None,
                'group': 'aaa',
                'data': {
                    'my_service_1_image': 'aaa',
                    'my_service_1_desired_count': 'aaa',
                    'my_service_1_random_variable': 'aaa',
                },
            },
            '/path/repo/2': {
                'path': '/path/repo/2',
                'git': None,
                'group': 'bbb',
                'data': {
                    'my_service_2_image': 'bbb',
                    'my_service_2_desired_count': 'bbb',
                    'my_service_2_random_variable': 'bbb',
                },
            },
        }

        result = config.get_services('aaa')
        expected_output = {
            'my_service_1': {
                'image': 'aaa', 'random_variable': 'aaa', 'desired_count': 'aaa'
            }
        }
        assert result == expected_output

    def test_get_services_empty_config(self):
        config = TFVarsConfig(None, [], load_config=False)
        config.data = {}

        result = config.get_services(None)
        expected_output = {}
        assert result == expected_output

    def test_get_service_names_should_give_all_services(self):
        config = TFVarsConfig(None, [], load_config=False)
        config.data = {
            '/path/repo/1': {
                'path': '/path/repo/1',
                'git': None,
                'group': 'aaa',
                'data': {
                    'my_service_1_image': 'aaa',
                    'my_service_1_desired_count': 'aaa',
                    'my_service_1_random_variable': 'aaa',
                    'my_service_2_image': 'aaa',
                    'my_service_2_desired_count': 'aaa',
                    'my_service_2_random_variable': 'aaa',
                    'my_service_3_image': 'aaa',
                    'my_service_3_desired_count': 'aaa',
                    'my_service_3_random_variable': 'aaa',
                    'my_service_4_image': 'aaa',
                    'my_service_4_desired_count': 'aaa',
                    'my_service_4_random_variable': 'aaa',
                    'my_service_5_image': 'aaa',
                    'my_service_5_desired_count': 'aaa',
                    'my_service_5_random_variable': 'aaa',
                },
            }
        }

        result = sorted(config.get_service_names())
        expected_output = sorted(['my_service_1', 'my_service_2', 'my_service_3', 'my_service_4', 'my_service_5'])
        assert result == expected_output

    def test_get_service_names_should_give_zero_serices(self):
        config = TFVarsConfig(None, [], load_config=False)
        config.data = {
            '/path/repo/1': {
                'path': '/path/repo/1',
                'git': None,
                'group': 'aaa',
                'data': {},
            }
        }

        result = config.get_service_names()
        expected_output = []
        assert result == expected_output


class TestTFVarsHelpers(object):
    def test_normalize_service_name_normal_case(self):
        result = TFVarsHelpers.normalize_service_name('my-custom-service123')
        expected_output = 'my_custom_service123'

        assert result == expected_output

    def test_get_artifact_key(self):
        result = TFVarsHelpers.get_artifact_key('my_custom_service')
        expected_output = 'my_custom_service_image'

        assert result == expected_output
