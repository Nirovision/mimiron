# -*- coding: utf-8 -*-
from . import Command as _Command
from .. import io

from ...vendor.terraform import TFVarsConfig


class Status(_Command):
    def _validate_and_configure(self):
        super(self.__class__, self)._validate_and_configure()

        self.tf = TFVarsConfig(self.tfvars_path)
        self.tf.load()

    def _run(self):
        services = self.tf.get_services()

        docker_org = self.config['DOCKER_ORG']
        table_data = [
            ['id', 'name', 'image tag (%s)' % docker_org, 'running', 'is active'],
        ]
        for i, service_name in enumerate(sorted(services.iterkeys()), 1):
            artifact = services[service_name]

            image_tag = artifact['image'].split(':')[-1]
            running = artifact['desired_count']
            is_active = 'yes' if int(running) > 0 else 'no'

            table_data.append([i, service_name, image_tag, running, is_active])

        io.info('displaying "%s" active&non-active services on %s' % (docker_org, self.env))
        io.print_table(table_data, 'current %s artifacts' % self.env)
        io.warn('only dockerized services are shown here currently...')
