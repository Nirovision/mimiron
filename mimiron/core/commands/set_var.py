# -*- coding: utf-8 -*-
import os

from . import Command as _Command
from ...vendor import git_extensions as git
from ...vendor import terraform
from .. import io


class SetVar(_Command):
    def _run(self):
        tfvars_file_name = self.config['TF_VARS_FILE_NAME']
        tfvars_path = os.path.join(self.repo.working_dir, tfvars_file_name)

        has_changes = git.sync_updates(self.repo)
        if has_changes:
            terraform.validate_tfvars(tfvars_path)
            io.info('successfully validated config path "%s"' % tfvars_path)

            message = 'chore(variables): updated %s config' % tfvars_file_name
            git.commit_and_push(self.repo, message)
        else:
            io.info('"%s" has no changes to commit' % tfvars_path)
        return None
