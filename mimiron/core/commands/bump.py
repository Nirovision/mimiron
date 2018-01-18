# -*- coding: utf-8 -*-
import humanize
from datetime import datetime

from mimiron.core.commands import Command as _Command
from mimiron.core import io

from mimiron.core.util.time import pretty_print_datetime
from mimiron.exceptions.vendor import NoChangesEmptyCommit
from mimiron.exceptions.commands import InvalidOperatingBranch

from mimiron.vendor import dockerhub
from mimiron.vendor.git_extensions import extensions as git_ext
from mimiron.vendor.terraform import TFVarsHelpers


class Bump(_Command):
    MAX_ARTIFACTS_SHOWN = 25

    def __init__(self, config, **kwargs):
        self.should_push = kwargs['should_push']
        self.service_name = kwargs['service']
        self.env = kwargs['env']
        service_name_normalized = TFVarsHelpers.normalize_service_name(self.service_name)
        self.artifact_key = TFVarsHelpers.get_artifact_key(service_name_normalized)

        super(Bump, self).__init__(config, **kwargs)

    def _prompt_artifact_selection(self, service_name, artifact_key, deployment_repo, env, artifacts):
        current_image = deployment_repo['tfvars'].get(artifact_key, env)

        io.info('found artifacts for "%s/%s"' % (self.config.get('dockerhub')['organization'], service_name,))
        table_data = [
            ('id', 'tag name (* = current)', 'created at', 'size',),
        ]
        for i, artifact in enumerate(artifacts, 1):
            created_at = datetime.strptime(artifact['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
            created_at = pretty_print_datetime(created_at)

            image_size = humanize.naturalsize(artifact['full_size'])
            image_name = artifact['name']
            if image_name in current_image:  # indicate the current artifact.
                image_name += ' *'

            table_data.append((str(i), image_name, created_at, image_size,))
        io.print_table(table_data, 'recent artifacts')

        # Handle the case where the selected artifact is the current artifact.
        selected_artifact = io.collect_input('select the artifact you want to use [q]:', artifacts)
        if selected_artifact and selected_artifact['name'] in current_image:
            io.err('selected artifact is already the current active artifact')
            return None
        return selected_artifact

    def _get_artifact(self, deployment_repo, dockerhub_auth, env):
        io.info('retrieving image tags for "%s" from dockerhub' % (self.service_name,))
        artifacts = dockerhub.list_image_tags(dockerhub_auth, self.service_name)
        artifacts = artifacts[:Bump.MAX_ARTIFACTS_SHOWN]

        if not artifacts:
            io.err('no artifacts found "%s/%s"' % (self.config.get('dockerhub')['organization'], self.service_name,))
            return None
        return self._prompt_artifact_selection(self.service_name, self.artifact_key, deployment_repo, env, artifacts)

    def _commit_bump(self, dockerhub_auth, deployment_repo, artifact, env):
        image_abspath = dockerhub.build_image_abspath(dockerhub_auth, self.service_name, artifact['name'])
        io.info('updating "%s"' % (image_abspath,))
        deployment_repo['tfvars'].set(self.artifact_key, image_abspath, env)
        deployment_repo['tfvars'].save()

        commit_message = git_ext.generate_service_bump_commit_message(
            deployment_repo['git'], self.service_name, env, artifact['name'],
        )

        did_commit = git_ext.commit_changes(deployment_repo['git'], commit_message)
        if not did_commit:
            raise NoChangesEmptyCommit('"%s" has nothing to commit' % (deployment_repo['git'].working_dir,))
        if env == 'production':
            git_ext.tag_commit(deployment_repo['git'], git_ext.generate_deploy_commit_tag(), commit_message)

    def run(self):
        io.info('authenticating "%s" against dockerhub' % (self.config.get('dockerhub')['organization'],))

        # Authenticate against DockerHub for artifact access.
        dockerhub_auth = dockerhub.DockerHubAuthentication(
            self.config.get('dockerhub')['username'],
            self.config.get('dockerhub')['password'],
            self.config.get('dockerhub')['organization'],
        )

        # Determine the deployment repo we want to make changes to.
        deployment_repo = TFVarsHelpers.find_deployment_repo(
            self.service_name, self.config.get('terraformRepositories')
        )
        if not deployment_repo:
            io.err('could not find service %r' % (self.service_name,))
            return None

        # Determine the environment and safe guard based on active branch.
        env = self.env or deployment_repo['defaultEnvironment']
        active_branch = deployment_repo['git'].active_branch.name
        if active_branch != deployment_repo['defaultGitBranch']:
            raise InvalidOperatingBranch(active_branch)

        # Select the artifact we want to bump with.
        artifact = self._get_artifact(deployment_repo, dockerhub_auth, env)
        if artifact is None:  # An artifact wasn't selected, end command.
            return None

        git_ext.sync_updates(deployment_repo['git'])
        deployment_repo['tfvars'].load()  # Reload tfvars in case the sync introduced new changes.

        # Update deployment repo and bump artifact.
        self._commit_bump(dockerhub_auth, deployment_repo, artifact, env)

        # Push changes up to GitHub to trigger changes in the build pipeline.
        if self.should_push:
            git_ext.push_commits(deployment_repo['git'])
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
