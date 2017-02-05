# -*- coding: utf-8 -*-
from . import Command as _Command
from ..environments import is_valid_env
from ...domain.commands import InvalidEnvironment


class Commit(_Command):
    def _validate_and_configure(self):
        if not is_valid_env(self.kwargs['env']):
            raise InvalidEnvironment(self.kwargs['env'])
        return True

    def _run(self):
        return True
