# -*- coding: utf-8 -*-


class Command(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self._validate_and_configure()
        self._run()

    def _validate_and_configure(self):
        raise NotImplementedError

    def _run(self):
        raise NotImplementedError
