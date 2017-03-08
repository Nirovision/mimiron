# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import tz

import humanize

from . import Command as _Command
from .. import io

from ...domain.vendor import NoChangesEmptyCommit
from ...vendor.terraform import TFVarsConfig
from ...vendor import dockerhub, git_extensions


class Bump(_Command):
    MAX_ARTIFACTS_SHOWN = 15

    def _validate_and_configure(self):
        super(self.__class__, self)._validate_and_configure()

        self.tf = TFVarsConfig(self.tfvars_path)
        self.tf.load()

        self.deployment_repo = self.config['TF_DEPLOYMENT_REPO']

        self.service_name = self.kwargs['service']
        self.service_name_normalized = self.tf.normalize_service_name(self.service_name)

        self.should_push = self.kwargs['should_push']
        self.is_latest = self.kwargs['is_latest']

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
            last_updated = datetime.strptime(artifact['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
            last_updated = last_updated.replace(tzinfo=tz.gettz('UTC'))
            last_updated = last_updated.astimezone(tz.tzlocal())

            last_updated_friendly = last_updated.strftime('%a %d %b, %I:%M%p')
            last_updated_humanized = humanize.naturaltime(last_updated.replace(tzinfo=None))

            updated_at = '%s (%s)' % (last_updated_friendly, last_updated_humanized)
            image_size = humanize.naturalsize(artifact['full_size'])
            image_name = artifact['name']
            if image_name in current_image:  # indicate the current artifact.
                image_name += ' *'

            table_data.append([i, image_name, updated_at, image_size])
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
        artifacts = artifacts[:self.__class__.MAX_ARTIFACTS_SHOWN]

        if not artifacts:
            io.err('no artifacts were found for "%s/%s"' % (self.config['DOCKER_ORG'], self.service_name))
            return None

        if self.is_latest:
            return self._prompt_latest_confirmation(artifacts)
        return self._prompt_artifact_selection(artifacts)

    def _run(self):
        artifact = self._get_artifact()

        if artifact is None:  # An artifact wasn't selected, end command.
            return None
        tag = artifact['name']

        git_extensions.sync_updates(self.deployment_repo)
        self.tf.load()

        image_abspath = dockerhub.build_image_abspath(self.auth, self.service_name, tag)
        io.info('updating "%s"' % image_abspath)

        self.tf.update_var(self.artifact_key, image_abspath)
        self.tf.save()

        commit_message = git_extensions.generate_service_bump_commit_message(
            self.deployment_repo, self.service_name, self.env, tag
        )
        did_commit = git_extensions.commit_changes(self.deployment_repo, commit_message)
        if not did_commit:
            raise NoChangesEmptyCommit('"%s" has nothing to commit' % self.deployment_repo.working_dir)

        if self.should_push:
            git_extensions.push_commits(self.deployment_repo)
        else:
            io.warn('commit to tfvars was NOT pushed to remote!')
            io.warn("it's your responsibility to bundle changes and explicitly push")
