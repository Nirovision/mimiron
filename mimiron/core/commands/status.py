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
        config = self.tf.config
        config = {k: v for k, v in config.iteritems() if k.endswith('_image')}

        table_data = [['name', 'image tag', 'artifact name']]
        for service_name in sorted(config.iterkeys()):
            artifact = config[service_name]
            image_tag = artifact.split(':')[-1]
            service_name = service_name.replace('_image', '')

            table_data.append([service_name, image_tag, artifact])

        io.info('displaying "%s" active&non-active services on %s' % (self.config['DOCKER_ORG'], self.env))
        io.print_table(table_data, 'current %s artifacts' % self.env)
