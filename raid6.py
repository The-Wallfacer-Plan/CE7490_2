#!/usr/bin/env python
from raid import RAID


# noinspection PyPep8Naming
class RAID6(RAID):
    def __init__(self, N):
        super(RAID6, self).__init__(N)

    def check(self, byte_nparray):
        pass

    def read(self, fname):
        pass

    def write(self, content, fname):
        pass
