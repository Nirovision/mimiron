# -*- coding: utf-8 -*-
from collections import namedtuple
from mimiron.vendor import dockerhub


class TestDockerHub(object):
    def setup_method(self):
        DockerAuthMock = namedtuple('DockerAuthMock', ['username', 'password', 'org'], verbose=True)
        self.auth = DockerAuthMock('example-username', 'example-password', 'imageintelligence')

    def test_build_image_abspath_normal_case(self):
        image_name = 'example-image'
        image_tag = '123123123'

        expected_output = '%s/%s:%s' % (self.auth.org, image_name, image_tag,)
        result = dockerhub.build_image_abspath(self.auth, image_name, image_tag,)

        assert result == expected_output
