# -*- coding: utf-8 -*-
import requests
import json


class DockerHubAuthentication(object):
    def __init__(self, username, password, org):
        self.username = username
        self.password = password
        self.org = org

        self._token = None

    def generate_token(self):
        payload = json.dumps({
            'username': self.username, 'password': self.password,
        })
        headers = {
            'Content-Type': 'application/json',
        }
        endpoint = 'https://hub.docker.com/v2/users/login/'

        response = requests.post(endpoint, data=payload, headers=headers)
        return response.json()['token'] if response.status_code == 200 else None

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
    response = method(endpoint, headers={'Authorization': 'JWT %s' % token})
    return response.json() if response.status_code == 200 else None


def list_image_repos(auth, page_size=100):
    endpoint = 'https://hub.docker.com/v2/repositories/%s/?page_size=%s' % (
        auth.org, page_size,
    )
    response = _api_request(endpoint, requests.get, auth)
    return response['results'] if response is not None else response


def list_image_tags(image_name, auth, page_size=100):
    endpoint = 'https://hub.docker.com/v2/repositories/%s/%s/tags/?page_size=%s' % (
        auth.org, image_name, page_size,
    )
    response = _api_request(endpoint, requests.get, auth)
    return response['results'] if response is not None else response
