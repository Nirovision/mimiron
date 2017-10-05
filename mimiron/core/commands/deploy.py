# -*- coding: utf-8 -*-
from . import Command as _Command
from .. import io
from ..util.time import pretty_print_datetime
from ...vendor.git_extensions import extensions as git_ext


class Deploy(_Command):
    MAX_SUMMARY_LIMIT = 50
    SHOW_LAST_LIMIT = 20

    def __init__(self, config, **kwargs):
        super(Deploy, self).__init__(config, **kwargs)

    def _prompt_repo_selection(self, deployment_repos):
        io.info('displaying all repositories specified in config')
        table_data = [
            ('id', 'path', 'default environment', 'tag environment', 'default git branch',),
        ]
        for i, deployment_repo in enumerate(deployment_repos, 1):
            table_data.append((
                str(i),
                deployment_repo['path'],
                deployment_repo['defaultEnvironment'] or io.add_color('n/a', 'red'),
                deployment_repo['tagEnvironment'] or io.add_color('n/a', 'red'),
                deployment_repo['defaultGitBranch'],
            ))

        io.print_table(table_data, 'deployment repositories')
        return io.collect_input(
            'select the target deployment repository [q]:',
            self.config.get('terraformRepositories'),
        )

    def _prompt_commit_selection(self, deployment_repo, show_last_limit):
        io.info('displaying @~%s most recent commits for "%s"' % (show_last_limit, deployment_repo['path'],))

        table_data = [
            ('id', 'commit id', 'message', 'author', 'committed at',),
        ]
        limit = Deploy.MAX_SUMMARY_LIMIT
        commits = []

        for i, commit in enumerate(deployment_repo['git'].iter_commits(max_count=show_last_limit), 1):
            message = commit.summary
            message = message[:limit].rstrip() + '...' if len(message) > limit else message

            table_data.append((
                str(i),
                commit.name_rev.split(' ')[0][:9],
                message,
                commit.author.name.strip('<>'),
                pretty_print_datetime(commit.committed_datetime),
            ))
            commits.append(commit)
        io.print_table(table_data, 'recent commits')
        return io.collect_input('select the commit you want to deploy [q]:', commits)

    def run(self):
        show_last_limit = int(self.kwargs['show_last_limit'] or self.SHOW_LAST_LIMIT)
        should_push = self.kwargs['should_push']
        is_tag = self.kwargs['is_tag']
        is_empty_commit = self.kwargs['is_empty_commit']

        deployment_repo = self._prompt_repo_selection(self.config.get('terraformRepositories'))
        if not deployment_repo:
            return None

        git_ext.sync_updates(deployment_repo['git'])
        deployment_repo['tfvars'].load()  # sync_updates may have changed tfvars.

        commit_message = git_ext.generate_commit_message(deployment_repo['git'])
        if is_empty_commit:
            commit = git_ext.commit_empty_changes(deployment_repo['git'], commit_message)
        else:
            commit = self._prompt_commit_selection(deployment_repo, show_last_limit)
        if not commit:
            io.info('no commit created or specified, exiting deploy')
            return None

        if is_tag:
            git_ext.tag_commit(
                deployment_repo['git'],
                git_ext.generate_deploy_commit_tag(),
                commit_message,
                ref=commit
            )

        if should_push:
            git_ext.push_commits(deployment_repo['git'])
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
