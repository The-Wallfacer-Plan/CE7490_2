#!/usr/bin/env python
import os

import config
import utils

MAX_SIZE = 10


# noinspection PyPep8Naming
class RAID(object):
    def __init__(self, N):
        self.N = N
        self.disk_path = os.path.join(config.root, self.__class__.__name__)
        self.data = [None] * N
        utils.init_disks(self.disk_path, self.N)

    def get_real_name(self, i, fname):
        return os.path.join(self.disk_path, config.disk_prefix + str(i), fname)

    @staticmethod
    def read_chunk(fpath, size):
        with open(fpath, 'rb') as rf:
            while True:
                chunk = rf.read(size)
                if chunk == '':
                    raise StopIteration
                yield chunk

    def contents(self, fpath):
        b = b''

    def read(self, fname):
        raise NotImplementedError

    def write(self, fname):
        raise NotImplementedError


# noinspection PyPep8Naming
class RAID4(RAID):
    def __init__(self, N):
        super(RAID4, self).__init__(N)

    def read(self, fname):
        for i in xrange(self.N):
            fpath = self.get_real_name(i, fname)
            with open(fpath, 'rb') as fh:
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
