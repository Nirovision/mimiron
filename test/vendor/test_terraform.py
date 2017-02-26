# -*- coding: utf-8 -*-
import pytest

from mimiron.vendor.terraform import TFVarsConfig


class TestTerraform(object):
    def setup_method(self):
        self.config = TFVarsConfig(None)
        self.config.has_loaded_config = True

    def test_normalize_service_name_normal_case(self):
        result = self.config.normalize_service_name('my-custom-service123')
        expected_output = 'my_custom_service123'

        assert result == expected_output

    def test_get_artifact_key_as_non_ami(self):
        result = self.config.get_artifact_key('my_custom_service', is_ami=False)
        expected_output = 'my_custom_service_image'

        assert result == expected_output

    def test_get_services_valid_config(self):
        self.config._config = {
            'my_service_1_image': 'xxx',
            'my_service_1_desired_count': 'yyy',
            'my_service_1_random_variable': 'zzz',

            'my_service_2_image': 'xxx',
            'my_service_2_desired_count': 'yyy',
            'my_service_2_random_variable': 'zzz',
        }

        result = self.config.get_services()
        expected_output = {
            'my_service_2': {
                'image': 'xxx', 'random_variable': 'zzz', 'desired_count': 'yyy'
            },
            'my_service_1': {
                'image': 'xxx', 'random_variable': 'zzz', 'desired_count': 'yyy'
            }
        }
        assert result == expected_output

    def test_get_services_empty_config(self):
        self.config._config = {}

        result = self.config.get_services()
        expected_output = {}
        assert result == expected_output
