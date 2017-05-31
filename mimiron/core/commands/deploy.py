# -*- coding: utf-8 -*-
from . import Command as _Command
from .. import io
from .. import constants as const
from ..util.time import pretty_print_datetime
from ...vendor.git_extensions import extensions as git_ext


class Deploy(_Command):
    MAX_SUMMARY_LIMIT = 50

    def validate_and_configure(self):
        super(self.__class__, self).validate_and_configure()

        self.show_last_limit = int(self.kwargs['show_last_limit'])
        self.should_push = self.kwargs['should_push']

    def _prompt_commit_selection(self):
        io.info('displaying @~%s most recent commits' % self.show_last_limit)
        table_data = [
            ['id', 'commit id', 'message', 'author', 'committed at'],
        ]
        limit = self.__class__.MAX_SUMMARY_LIMIT

        commits = []
        for i, commit in enumerate(self.deployment_repo.iter_commits(max_count=self.show_last_limit), 1):
            message = commit.summary
            message = message[:limit] + '...' if len(message) > limit else message

            table_data.append([
                i,
                commit.name_rev.split(' ')[0][:9],
                message,
                commit.author.name.strip('<>'),
                pretty_print_datetime(commit.committed_datetime)
            ])
            commits.append(commit)

        io.print_table(table_data, 'recent commits')
        return io.collect_input('select the commit you want to deploy [q]:', commits)

    def run(self):
        git_ext.sync_updates(self.deployment_repo)

        commit_message = git_ext.generate_commit_message(self.deployment_repo, self.env)
        if self.env == const.PRODUCTION:
            commit = self._prompt_commit_selection()
            if not commit:
                return None
            git_ext.tag_commit(
                self.deployment_repo,
                git_ext.generate_deploy_commit_tag(),
                commit_message,
                ref=commit
            )
        else:
            git_ext.commit_empty_changes(self.deployment_repo, commit_message)

        if self.should_push:
            git_ext.push_commits(self.deployment_repo)
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
