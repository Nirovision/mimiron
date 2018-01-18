# -*- coding: utf-8 -*-
from mimiron.core.commands import Command as _Command
from mimiron.core import io
from mimiron.core.util.time import pretty_print_datetime
from mimiron.exceptions.commands import InvalidOperatingBranch
from mimiron.vendor.git_extensions import extensions as git_ext


class Deploy(_Command):
    MAX_SUMMARY_LIMIT = 50

    def __init__(self, config, **kwargs):
        self.should_push = kwargs['should_push']
        self.env = kwargs['env']
        self.is_empty_commit = kwargs['is_empty_commit']

        super(Deploy, self).__init__(config, **kwargs)

    def _prompt_repo_selection(self, deployment_repos):
        io.info('displaying all repositories specified in config')
        table_data = [
            ('id', 'path', 'default environment', 'default git branch',),
        ]
        for i, deployment_repo in enumerate(deployment_repos, 1):
            table_data.append((
                str(i),
                deployment_repo['path'],
                deployment_repo['defaultEnvironment'] or io.add_color('n/a', 'red'),
                deployment_repo['defaultGitBranch'],
            ))

        io.print_table(table_data, 'deployment repositories')
        return io.collect_input(
            'select the target deployment repository [q]:',
            self.config.get('terraformRepositories'),
        )

    def _prompt_commit_selection(self, deployment_repo, show_last_limit=50):
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

    def _select_commit(self, deployment_repo):
        commit_message = git_ext.generate_commit_message(deployment_repo['git'])
        commit = None

        # Production and we want to deploy the latest changes without explicitly specifying.
        if self.env == 'production' and self.is_empty_commit:
            commit = git_ext.commit_empty_changes(deployment_repo['git'], commit_message)

        # Production and we want to rollback or select a specific commit.
        if self.env == 'production' and not self.is_empty_commit:
            commit = self._prompt_commit_selection(deployment_repo)

        # Not production, re-deploy - no staging rollbacks (i.e. only way to trigger build, generate a new commit).
        if self.env != 'production':
            commit = git_ext.commit_empty_changes(deployment_repo['git'], commit_message)

        # We're in production so let's tag the commit we just made or selected.
        if self.env == 'production' and commit:
            git_ext.tag_commit(
                deployment_repo['git'],
                git_ext.generate_deploy_commit_tag(),
                commit_message,
                ref=commit
            )
        return commit

    def run(self):
        deployment_repo = self._prompt_repo_selection(self.config.get('terraformRepositories'))
        if not deployment_repo:
            return None

        # Safe guard commits based on active branch.
        active_branch = deployment_repo['git'].active_branch.name
        if active_branch != deployment_repo['defaultGitBranch']:
            raise InvalidOperatingBranch(active_branch)

        git_ext.sync_updates(deployment_repo['git'])
        deployment_repo['tfvars'].load()  # sync_updates may have changed tfvars.

        commit = self._select_commit(deployment_repo)
        if not commit:
            io.info('no commit created or specified, exiting deploy')
            return None
        if self.should_push:
            git_ext.push_commits(deployment_repo['git'])
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
