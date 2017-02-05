# -*- coding: utf-8 -*-


class Command(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.validate()
        self.run()

    def validate(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
