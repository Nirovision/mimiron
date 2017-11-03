# -*- coding: utf-8 -*-
import time
from .. import io


class Command(object):
    def __init__(self, config, **kwargs):
        self.kwargs = kwargs
        self.config = config

        start_time = time.time()
        self.run()
        total_time = (time.time() - start_time) * 1000

        io.info(u'\U0001F916  Mimiron completed operation in %0.3fms' % total_time)

    def run(self):
        raise NotImplementedError
