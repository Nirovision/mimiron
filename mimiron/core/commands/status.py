# -*- coding: utf-8 -*-
from . import Command as _Command
from .. import io

from ...vendor.terraform import TFVarsConfig
from ...vendor.git_extensions import extensions as git_ext


class Status(_Command):
    def validate_and_configure(self):
        super(self.__class__, self).validate_and_configure()

        self.tf = TFVarsConfig(self.tfvars_path)

    def _format_row(self, artifact):
        image_tag = artifact['image'].split(':')[-1]
        desired_count = int(artifact.get('desired_count', 0))
        if desired_count == 0:
            desired_count = io.add_color('zero', 'red')

        cpu = artifact.get('cpu', io.add_color('n/a', 'red'))
        memory = artifact.get('memory', io.add_color('n/a', 'red'))
        return [image_tag, desired_count, cpu, memory]

    def run(self):
        git_ext.sync_updates(self.deployment_repo)
        self.tf.load()  # sync_updates may have changed tfvars

        services = self.tf.get_services()

        docker_org = self.config['DOCKER_ORG']
        table_data = [
            ['id', 'name', 'image tag (%s)' % docker_org, 'desired count', 'cpu units', 'memory (mb)'],
        ]
        for i, service_name in enumerate(sorted(services.iterkeys()), 1):
            artifact = services[service_name]
            table_data.append([i, service_name] + self._format_row(artifact))

        io.info('displaying "%s" active&inactive services on %s' % (docker_org, self.env))
        io.print_table(table_data, 'current %s artifacts' % self.env)
        io.warn('only dockerized services are shown here (i.e. no lambda or ami)')
