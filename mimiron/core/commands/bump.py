# -*- coding: utf-8 -*-
import humanize
from datetime import datetime

from . import Command as _Command
from .. import io

from ..util.time import pretty_print_datetime
from ...exceptions.vendor import NoChangesEmptyCommit
from ...exceptions.commands import InvalidOperatingBranch

from ...vendor import dockerhub
from ...vendor.git_extensions import extensions as git_ext

from ...vendor.terraform import TFVarsHelpers


class Bump(_Command):
    MAX_ARTIFACTS_SHOWN = 20

    def __init__(self, config, **kwargs):
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

    def _get_artifact(self, service_name, artifact_key, deployment_repo, dockerhub_auth, env, is_show_all):
        io.info('retrieving image tags for "%s" from dockerhub' % (service_name,))
        artifacts = dockerhub.list_image_tags(dockerhub_auth, service_name)

        # Truncate artifacts we get from DockerHub to make it more readable.
        if not is_show_all:
            artifacts = artifacts[:Bump.MAX_ARTIFACTS_SHOWN]

        if not artifacts:
            io.err('no artifacts were found for "%s/%s"' % (self.config.get('dockerhub')['organization'], service_name,))
            return None

        return self._prompt_artifact_selection(service_name, artifact_key, deployment_repo, env, artifacts)

    def run(self):
        service_name = self.kwargs['service']
        service_name_normalized = TFVarsHelpers.normalize_service_name(service_name)
        artifact_key = TFVarsHelpers.get_artifact_key(service_name_normalized)

        should_push = self.kwargs['should_push']
        is_show_all = self.kwargs['is_show_all']

        io.info('authenticating "%s" against dockerhub' % (self.config.get('dockerhub')['organization'],))
        dockerhub_auth = dockerhub.DockerHubAuthentication(
            self.config.get('dockerhub')['username'],
            self.config.get('dockerhub')['password'],
            self.config.get('dockerhub')['organization'],
        )

        deployment_repo = TFVarsHelpers.find_deployment_repo(service_name, self.config.get('terraformRepositories'))
        if not deployment_repo:
            io.err('could not find service %r' % (service_name,))
            return None

        env = self.kwargs['env'] or deployment_repo['defaultEnvironment']
        tag = self.kwargs['tag']

        active_branch = deployment_repo['git'].active_branch.name
        if active_branch != deployment_repo['defaultGitBranch']:
            raise InvalidOperatingBranch(active_branch)

        artifact = self._get_artifact(
            service_name,
            artifact_key,
            deployment_repo,
            dockerhub_auth,
            env,
            is_show_all,
        )
        if artifact is None:  # An artifact wasn't selected, end command.
            return None

        git_ext.sync_updates(deployment_repo['git'])
        deployment_repo['tfvars'].load()  # Reload tfvars in case the sync introduced new changes.

        image_abspath = dockerhub.build_image_abspath(
            dockerhub_auth,
            service_name,
            artifact['name'],
        )
        io.info('updating "%s"' % (image_abspath,))
        deployment_repo['tfvars'].set(artifact_key, image_abspath, env)
        deployment_repo['tfvars'].save()

        commit_message = git_ext.generate_service_bump_commit_message(
            deployment_repo['git'], service_name, env, artifact['name']
        )
        did_commit = git_ext.commit_changes(deployment_repo['git'], commit_message)

        if not did_commit:
            raise NoChangesEmptyCommit('"%s" has nothing to commit' % (deployment_repo['git'].working_dir,))

        if env and env == deployment_repo['tagEnvironment'] and tag:
            git_ext.tag_commit(
                deployment_repo['git'],
                git_ext.generate_deploy_commit_tag(),
                commit_message
            )
        elif env != deployment_repo['tagEnvironment'] and tag:
            io.warn('cannot tag bump operation when env is NOT "%s"' % deployment_repo['tagEnvironment'])

        if should_push:
            git_ext.push_commits(deployment_repo['git'])
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
