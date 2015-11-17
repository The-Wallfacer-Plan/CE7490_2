#!/usr/bin/env python

import os
import random
import string

import config
from log_helper import get_logger, init_logger
from raid4 import RAID4
from raid5 import RAID5
from raid6 import RAID6


def gen_rnd_file(fname, size, content_type):
    if content_type == 'text':
        # noinspection PyUnusedLocal
        content = ''.join([random.choice(string.ascii_letters) for i in xrange(size)])
    else:
        content = os.urandom(size)
    fpath = os.path.join(config.root, fname)
    if os.path.isfile(fpath):
        file_size = os.stat(fpath).st_size
        if file_size == size:
            get_logger().warning('fname={} with size={} exists'.format(fname, size))
            return
    with open(fpath, 'wb') as fout:
        fout.write(content)


# noinspection PyUnusedLocal
def starter():
    if not os.path.isdir(config.root):
        os.mkdir(config.root)
    r4 = RAID4(config.N)
    r5 = RAID4(config.N)
    r6 = RAID6(config.N)
    gen_rnd_file('data1', SIZE, 'text')
    gen_rnd_file('data2', SIZE, 'bin')


SIZE = 4096

if __name__ == '__main__':
    init_logger()
    starter()
    for fname in ['data1', 'data2']:
        fpath = os.path.join(config.root, fname)
        with open(fpath, 'rb') as fh:
            content = fh.read()
        for raid_type in [RAID4, RAID5]:
            raid = raid_type(4)
            raid.write(content, fname)
            size = len(content)
            content_raid = raid.read(fname, size)
            assert content == content_raid
            error_index = 2
            raid.recover(fname, error_index)
