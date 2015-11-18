#!/usr/bin/env python
from __future__ import print_function

import operator
import os

import numpy as np
from BitVector import BitVector

import config
# noinspection PyPep8Naming
from gf8 import GF
from log_helper import init_logger, get_logger


class RAIDCheckError(Exception):
    def __init__(self, msg):
        super(RAIDCheckError, self).__init__(msg)


def init_disks(root_path, N):
    if not os.path.isdir(root_path):
        os.mkdir(root_path)
    for i in xrange(N):
        fname = config.disk_prefix + str(i)
        fpath = os.path.join(root_path, fname)
        if not os.path.isdir(fpath):
            os.mkdir(fpath)


def read_content(fpath):
    with open(fpath, 'rb') as fh:
        return fh.read()


def write_content(fpath, content):
    with open(fpath, 'wb') as fh:
        fh.write(content)


def gen_p(data_ndarray):
    """
    :param data_ndarray: the data array
    :return: the parity of the data_ndarray
    """
    res = np.bitwise_xor.reduce(data_ndarray)
    assert res.ndim == 1
    new_num = res.shape[0]
    res.shape = (1, new_num)
    return res


def gen_q(data_ndarray):
    """
    :param data_ndarray: the data ndarray
    :return: q_ndarray with shape=(1, byte_ndarray.shape[1])
    """
    transposed = np.transpose(data_ndarray)
    # print(data_ndarray.shape)
    get_logger().info('transposed\n{}'.format(transposed))
    gf = GF()
    q_list = []
    for _1darray in transposed:
        bv_list = []
        for i, arr_val in enumerate(_1darray):
            res_i = gf.multiply(gf.generator[i % gf.circle], BitVector(intVal=arr_val))
            # print('i={}, arr_val={}, res_i={}'.format(i, arr_val, res_i))
            bv_list.append(res_i)
            # map(lambda i: print(i), bv_list)
        q_value = reduce(operator.xor, bv_list).int_val()
        q_list.append(q_value)
    arr = np.array(q_list, ndmin=2)
    assert arr.shape[1] == data_ndarray.shape[1]
    # arr = np.zeros((1, byte_ndarray.shape[1]), byte_ndarray.dtype)
    return arr


def check_data_p(byte_ndarray):
    res = np.bitwise_xor.reduce(byte_ndarray)
    if np.count_nonzero(res) != 0:
        msg = 'xor of arrays not all zeros, res={}'.format(res)
        raise RAIDCheckError(msg)


def check_q(data_ndarray, q_ndarray):
    computed = gen_q(data_ndarray)
    if not np.array_equal(computed, q_ndarray):
        msg = 'Q check failed, q_ndarray={}, computed={}'.format(q_ndarray, computed)
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
