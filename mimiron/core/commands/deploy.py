# -*- coding: utf-8 -*-
from . import Command as _Command


class Deploy(_Command):
    def validate(self):
        pass

    def run(self):
        return True
