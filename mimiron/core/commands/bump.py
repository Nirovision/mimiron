# -*- coding: utf-8 -*-
import humanize
from datetime import datetime

from . import Command as _Command
from .. import io

from .. import constants as const

from ..util.time import pretty_print_datetime
from ...domain.vendor import NoChangesEmptyCommit

from ...vendor.terraform import TFVarsConfig
from ...vendor import dockerhub
from ...vendor.git_extensions import extensions as git_ext


class Bump(_Command):
    MAX_ARTIFACTS_SHOWN = 20

    def validate_and_configure(self):
        super(self.__class__, self).validate_and_configure()

        self.tf = TFVarsConfig(self.tfvars_path)
        self.tf.load()

        self.service_name = self.kwargs['service']
        self.service_name_normalized = self.tf.normalize_service_name(self.service_name)

        self.should_push = self.kwargs['should_push']
        self.is_latest = self.kwargs['is_latest']
        self.is_show_all = self.kwargs['is_show_all']

        self.artifact_key = self.tf.get_artifact_key(self.service_name_normalized)

        io.info('authenticating "%s" against dockerhub' % self.config['DOCKER_ORG'])
        self.auth = dockerhub.DockerHubAuthentication(
            self.config['DOCKER_USERNAME'],
            self.config['DOCKER_PASSWORD'],
            self.config['DOCKER_ORG']
        )

    def _prompt_artifact_selection(self, artifacts):
        current_image = self.tf.get_var(self.artifact_key)

        io.info('found artifacts for "%s/%s"' % (self.config['DOCKER_ORG'], self.service_name))
        table_data = [
            ['id', 'tag name (* = current)', 'created at', 'size'],
        ]
        for i, artifact in enumerate(artifacts, 1):
            created_at = datetime.strptime(artifact['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
            created_at = pretty_print_datetime(created_at)

            image_size = humanize.naturalsize(artifact['full_size'])
            image_name = artifact['name']
            if image_name in current_image:  # indicate the current artifact.
                image_name += ' *'

            table_data.append([i, image_name, created_at, image_size])
        io.print_table(table_data, 'recent artifacts')

        # Handle the case where the selected artifact is the current artifact.
        selected_artifact = io.collect_input('select the artifact you want to use [q]:', artifacts)
        if selected_artifact and selected_artifact['name'] in current_image:
            io.err('selected artifact is already the current active artifact')
            return None
        return selected_artifact

    def _prompt_latest_confirmation(self, artifacts):
        latest_artifact = artifacts[0]
        tag = latest_artifact['name']

        input_ = io.collect_single_input('are you sure (latest: %s)? [y/n/q]:' % tag)
        if input_ not in ['y', None]:
            return None
        return latest_artifact

    def _get_artifact(self):
        io.info('retrieving image tags for "%s" from dockerhub' % self.service_name)
        artifacts = dockerhub.list_image_tags(self.auth, self.service_name)

        # Truncate artifacts we get from DockerHub to make it more readable.
        if not self.is_show_all:
            artifacts = artifacts[:self.__class__.MAX_ARTIFACTS_SHOWN]

        if not artifacts:
            io.err('no artifacts were found for "%s/%s"' % (self.config['DOCKER_ORG'], self.service_name))
            return None

        if self.is_latest:
            return self._prompt_latest_confirmation(artifacts)
        return self._prompt_artifact_selection(artifacts)

    def run(self):
        artifact = self._get_artifact()

        if artifact is None:  # An artifact wasn't selected, end command.
            return None
        tag = artifact['name']

        git_ext.sync_updates(self.deployment_repo)
        self.tf.load()

        image_abspath = dockerhub.build_image_abspath(self.auth, self.service_name, tag)
        io.info('updating "%s"' % image_abspath)

        self.tf.update_var(self.artifact_key, image_abspath)
        self.tf.save()

        commit_message = git_ext.generate_service_bump_commit_message(
            self.deployment_repo, self.service_name, self.env, tag
        )
        did_commit = git_ext.commit_changes(self.deployment_repo, commit_message)

        if not did_commit:
            raise NoChangesEmptyCommit('"%s" has nothing to commit' % self.deployment_repo.working_dir)

        if self.env == const.PRODUCTION and did_commit:
            git_ext.tag_commit(
                self.deployment_repo,
                git_ext.generate_deploy_commit_tag(),
                commit_message
            )

        if self.should_push:
            git_ext.push_commits(self.deployment_repo)
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
