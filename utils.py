#!/usr/bin/env python
import os

import config


# noinspection PyPep8Naming
def init_disks(name, N):
    disk_path = os.path.join(config.root, name)
    if not os.path.isdir(disk_path):
        os.mkdir(disk_path)
    for i in xrange(N):
        fname = config.disk_prefix + str(i)
        fpath = os.path.join(disk_path, fname)
        if not os.path.isfile(fpath):
            os.mkdir(fpath)
