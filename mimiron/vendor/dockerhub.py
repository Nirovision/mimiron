# -*- coding: utf-8 -*-
import requests
import json

from ..domain.vendor import InvalidDockerHubCredentials
from ..domain.vendor import DockerConnectionError


class DockerHubAuthentication(object):
    def __init__(self, username, password, org, generate_token=True):
        self.username = username
        self.password = password
        self.org = org

        self._token = None
        if generate_token:
            self._token = self.generate_token()

    def generate_token(self):
        payload = json.dumps({
            'username': self.username, 'password': self.password,
        })
        headers = {
            'Content-Type': 'application/json',
        }
        endpoint = 'https://hub.docker.com/v2/users/login/'

        try:
            response = requests.post(endpoint, data=payload, headers=headers)
            if response.status_code == 200:
                return response.json()['token']
            raise InvalidDockerHubCredentials
        except requests.exceptions.ConnectionError:
            raise DockerConnectionError

    @property
    def token(self):
        if not self._token:
            self._token = self.generate_token()
        return self._token

    @token.setter
    def token(self, new_token):
        self._token = new_token


def _api_request(endpoint, method, auth):
    token = auth.token
    if token is None:
        return None

    try:
        response = method(endpoint, headers={'Authorization': 'JWT %s' % token})
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        raise DockerConnectionError


def list_repositories(auth, page_size=100):
    endpoint = 'https://hub.docker.com/v2/repositories/%s/?page_size=%s' % (
        auth.org, page_size,
    )
    response = _api_request(endpoint, requests.get, auth)
    return response['results'] if response is not None else response


def list_image_tags(auth, image_name, page_size=100):
    endpoint = 'https://hub.docker.com/v2/repositories/%s/%s/tags/?page_size=%s' % (
        auth.org, image_name, page_size,
    )
    response = _api_request(endpoint, requests.get, auth)
    return response['results'] if response is not None else response


def build_image_abspath(auth, image_name, tag):
    return auth.org + '/' + image_name + ':' + tag
