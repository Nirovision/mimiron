# -*- coding: utf-8 -*-
from . import Command as _Command


class Deploy(_Command):
    def _validate_and_configure(self):
        pass

    def _run(self):
        return True
