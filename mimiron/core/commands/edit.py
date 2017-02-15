# -*- coding: utf-8 -*-
import os
import subprocess

from . import Command as _Command
from .. import io


class Edit(_Command):
    def _run(self):
        io.info('preparing to open config for "%s"' % self.env)

        config_var_path = os.path.join(self.repo.working_dir, 'variables.json')
        if not os.path.isfile(config_var_path):
            io.err('failed to open "%s" (not a file)' % config_var_path)
        else:
            io.info('opening "%s"' % config_var_path)
            subprocess.call([self.config['EDITOR'], config_var_path])
        io.info('closed "%s" config, finished editing' % self.env)
