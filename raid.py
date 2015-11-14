#!/usr/bin/env python
import os

import config
import utils


# noinspection PyPep8Naming
class RAID(object):
    def __init__(self, N):
        self.name = self.__class__.__name__
        self.nodes = N
        utils.init_disks(self.name, self.nodes)

    def get_real_name(self, i, fname):
        return os.path.join(self.name, config.disk_prefix + str(i), fname)

    def read(self, fname):
        raise NotImplementedError

    def write(self, fname):
        raise NotImplementedError


# noinspection PyPep8Naming
class RAID4(RAID):
    def __init__(self, N):
        super(RAID4, self).__init__(N)

    def read(self, fname):
        pass

    def write(self, fname):
        pass


# noinspection PyPep8Naming
class RAID6(RAID):
    def __init__(self, N):
        super(RAID6, self).__init__(N)

    def read(self, fname):
        pass

    def write(self, fname):
        pass
