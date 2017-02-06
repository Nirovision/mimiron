# -*- coding: utf-8 -*-
import os

from . import Command as _Command
from .. import io
from ..environments import get_env_repo_name
from ...vendor import git_extensions as git


class Deploy(_Command):
    def _validate_and_configure(self):
        super(self.__class__, self)._validate_and_configure()

        self.deploy_repo = self.config['TF_DEPLOYMENT_REPO']
        self.should_push = self.kwargs['should_push']

    def _prompt_recent_commits(self, commits):
        repo_name = os.path.split(self.repo.working_dir)[-1]
        io.info('listing recent commits for "%s"' % repo_name)

        table_data = [
            ['id', 'commit', 'committed at', 'author (name)'],
        ]
        for i, c in enumerate(commits, 1):
            sha = c.name_rev.split(' ')[0][:10]
            authored_at = c.authored_datetime.strftime('%a %d %b, %I:%M%p')
            table_data.append([i, sha, authored_at, c.author.name])

        io.print_table(table_data, 'recent commits')
        return io.collect_input('select the commit sha you want to update [q]:', commits)

    def _run(self):
        git.sync_updates(self.repo)
        git.sync_updates(self.deploy_repo)

        recent_commits = git.get_recent_commits(self.repo)
        commit = self._prompt_recent_commits(recent_commits)
        if commit is None:
            return None

        submodule_name = get_env_repo_name(self.env)
        commit_sha = commit.name_rev.split(' ')[0]
        has_changes = git.sync_submodule_updates(self.deploy_repo, submodule_name, commit_sha)

        if not has_changes:
            return None

        message = 'chore(tfvars): bump %s.tfvars %s' % (self.env, commit_sha[:10])
        if self.should_push:
            git.commit_and_push(self.deploy_repo, message)
        else:
            git.commit_changes(self.deploy_repo, message)
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle more changes and explicitly push")
