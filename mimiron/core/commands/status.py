# -*- coding: utf-8 -*-
from mimiron.core.commands import Command as _Command
from mimiron.core import io
from mimiron.vendor.git_extensions import extensions as git_ext


class Status(_Command):
    def __init__(self, config, **kwargs):
        self.env = kwargs['env']
        super(Status, self).__init__(config, **kwargs)

    def _format_row(self, index, service_name, artifact):
        image_tag = artifact['image'].split(':')[-1]
        desired_count = int(artifact.get('desired_count', 0))
        if desired_count == 0:
            desired_count = io.add_color('zero', 'red')

        cpu = artifact.get('cpu', io.add_color('n/a', 'red'))
        memory = artifact.get('memory', io.add_color('n/a', 'red'))
        return str(index), service_name, image_tag, desired_count, cpu, memory,

    def _build_status_table(self, deployment_repo, env):
        services = deployment_repo['tfvars'].get_services(env)
        docker_org = self.config.get('dockerhub')['organization']
        table_data = [
            ('id', 'name', 'image tag (%s)' % (docker_org,), 'desired count', 'cpu units', 'memory (mb)',),
        ]
        for i, service_name in enumerate(sorted(services.iterkeys()), 1):
            artifact = services[service_name]
            table_data.append(self._format_row(i, service_name, artifact))
        return table_data

    def run(self):
        io.info('performing git sync across all specified repositories...')
        for deployment_repo in self.config.get('terraformRepositories'):
            git_ext.sync_updates(deployment_repo['git'])
            deployment_repo['tfvars'].load()  # sync_updates may have changed tfvars.

            env = self.env or deployment_repo['defaultEnvironment']
            table_data = self._build_status_table(deployment_repo, env)
            docker_org = self.config.get('dockerhub')['organization']
            io.info('displaying "%s" active&inactive services on "%s"' % (docker_org, env,))
            io.print_table(table_data, 'current %s artifacts' % (env,))
        io.warn('only dockerized services are shown here (i.e. no lambda)')
