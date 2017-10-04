# -*- coding: utf-8 -*-


class Command(object):
    def __init__(self, config, **kwargs):
        self.kwargs = kwargs
        self.config = config

        self.validate_and_configure()
        self.run()

    def validate_and_configure(self):
        pass

    def run(self):
        raise NotImplementedError
