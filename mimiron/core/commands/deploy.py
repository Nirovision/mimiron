# -*- coding: utf-8 -*-
from . import Command as _Command


class Deploy(_Command):
    def _run(self):
        """
        TODO:

        determine the environment
        pull the repo we care about
        load the hcl var file as json
        determine the service we want to update
        make a request on dockerhub to pull down tags for environment
        prompt user to select a tag
        search for the associated var to update
        save hcl file
        set the commit as chore(services): bump <service> image tag <id>
        do a set_var and push
        get the new sha of the commit we just made
        do a set_sha and push
        """
        pass
