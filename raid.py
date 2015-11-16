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

    @staticmethod
    def _contents(fpath):
        with open(fpath, 'rb') as fh:
            return fh.read()

    def check(self, byte_nparray):
        raise NotImplementedError

    def read(self, fname):
        raise NotImplementedError

    def write(self, content, fname):
        raise NotImplementedError
