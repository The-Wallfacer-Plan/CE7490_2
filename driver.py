#!/usr/bin/env python

import os
import random
import string

import config
from raid4 import RAID4
from raid6 import RAID6


def gen_rnd_file(fname, size, content_type):
    if content_type == 'text':
        # noinspection PyUnusedLocal
        content = ''.join([random.choice(string.ascii_letters) for i in xrange(size)])
    else:
        content = os.urandom(size)
    fpath = os.path.join(config.root, fname)
    with open(fpath, 'wb') as fout:
        fout.write(content)


# noinspection PyUnusedLocal
def starter():
    if not os.path.isdir(config.root):
        os.mkdir(config.root)
    r4 = RAID4(config.N)
    r6 = RAID6(config.N)
    gen_rnd_file('data1', 19, 'text')
    gen_rnd_file('data2', 21, 'bin')


if __name__ == '__main__':
    starter()
    fname = 'data1'
    fpath = os.path.join(config.root, fname)
    with open(fpath, 'rb') as fh:
        content = fh.read()
    r4 = RAID4(3)
    r4.write(content, fname)
    content_r4 = r4.read(fname)
    print(content, content_r4)
