# -*- coding: utf-8 -*-
from ...config import config


class Command(object):
    def __init__(self, conf=config, **kwargs):
        self.kwargs = kwargs
        self.config = conf

        self._validate_and_configure()
        self._run()

    def _validate_and_configure(self):
        raise NotImplementedError

    def _run(self):
        raise NotImplementedError
