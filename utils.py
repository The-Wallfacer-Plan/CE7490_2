#!/usr/bin/env python
import os

import config


# noinspection PyPep8Naming
def init_disks(root_path, N):
    if not os.path.isdir(root_path):
        os.mkdir(root_path)
    for i in xrange(N):
        fname = config.disk_prefix + str(i)
        fpath = os.path.join(root_path, fname)
        if not os.path.isdir(fpath):
            os.mkdir(fpath)




class ParityCheckError(Exception):
    def __init__(self, msg):
        super(ParityCheckError, self).__init__(msg)
