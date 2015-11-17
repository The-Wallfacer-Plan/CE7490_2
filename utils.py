#!/usr/bin/env python
import os

import numpy as np

import config
# noinspection PyPep8Naming
from log_helper import init_logger


def init_disks(root_path, N):
    if not os.path.isdir(root_path):
        os.mkdir(root_path)
    for i in xrange(N):
        fname = config.disk_prefix + str(i)
        fpath = os.path.join(root_path, fname)
        if not os.path.isdir(fpath):
            os.mkdir(fpath)


def parity(byte_ndarray):
    res = np.bitwise_xor.reduce(byte_ndarray)
    assert res.ndim == 1
    new_num = res.shape[0]
    res.shape = (1, new_num)
    return res


def check_data_p(byte_ndarray):
    res = np.bitwise_xor.reduce(byte_ndarray)
    if np.count_nonzero(res) != 0:
        msg = 'xor of arrays not all zeros, res={}'.format(res)
        raise RAIDCheckError(msg)


def simple_test(raid_level, test_recovery=True):
    init_logger()
    raid = raid_level(4)
    data_fname = 'good.dat'
    original_content = 'good_morning_sir'
    # original_content = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13'
    size = len(original_content)
    raid.write(original_content, data_fname)
    raid_content = raid.read(data_fname, size)
    print(raid_content.__repr__())
    assert raid_content == original_content
    if test_recovery:
        error_index = 2
        raid.recover(data_fname, error_index)


def gf(byte_ndarray):
    """
    :param byte_ndarray: the data ndarray
    :return: q_ndarray with shape=(1, byte_ndarray.shape[1])
    """
    arr = np.zeros((1, byte_ndarray.shape[1]), byte_ndarray.dtype)
    return arr


def check_q(data_ndarray, q_ndarray):
    computed = gf(data_ndarray)
    if not np.array_equal(computed, q_ndarray):
        msg = 'Q check failed, q_ndarray={}, computed={}'.format(q_ndarray, computed)
        raise RAIDCheckError(msg)


class RAIDCheckError(Exception):
    def __init__(self, msg):
        super(RAIDCheckError, self).__init__(msg)
