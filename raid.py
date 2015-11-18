#!/usr/bin/env python
import os
from itertools import repeat

import numpy as np

import config
import utils
# noinspection PyPep8Naming
from log_helper import get_logger


# noinspection PyPep8Naming
class RAID(object):
    def __init__(self, N):
        self.BYTE_TYPE = np.int
        self.EOF = -1
        self.ZERO = 0
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

    def _read_n(self, fname, N, exclude=None):
        """
        generate nparray with dtype=BYTE_TYPE
        :param fname:
        :return: ndarray with shape=(n, length)
        """
        content_list = []
        for i in xrange(N):
            if (isinstance(exclude, int) and i == exclude) or (isinstance(exclude, list) and i in exclude):
                content_list.append(list())
            else:
                fpath = self.get_real_name(i, fname)
                content_list.append(self._contents(fpath))
        get_logger().info(content_list)
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # list of bytes (int) list
        byte_list = []
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.ZERO] * (length - len(content))
            byte_list.append(current_str_list)
        # bytes array
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        return byte_nparray

    def _gen_ndarray_from_content(self, content, num):
        # gen N-1 length empty list
        content_list = [[] for i in repeat(None, num)]
        for i in xrange(len(content)):
            mod_i = i % num
            content_list[mod_i].append(content[i])
        byte_list = []
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # fill 0
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.ZERO] * (length - len(content))
            byte_list.append(current_str_list)
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        get_logger().info('byte_array'.format(byte_nparray))
        return byte_nparray

    def _1darray_to_str(self, _1darray):
        real_write_content = filter(lambda b: b >= self.ZERO, _1darray)
        str_list = [chr(b) for b in real_write_content]
        return ''.join(str_list)

    def _write_n(self, fname, write_array, N):
        r"""
        doesn't care about trailing '\x0'
        :param fname:
        :param write_array:
        :return:
        """
        get_logger().info('write_array:\n{}'.format(write_array))
        # write N
        assert write_array.shape[0] == N
        for j in range(N):
            fpath = self.get_real_name(j, fname)
            content_i = self._1darray_to_str(write_array[j])
            with open(fpath, 'wb') as fh:
                fh.write(content_i)

    def check(self, byte_ndarray):
        raise NotImplementedError

    def recover(self, fname, exclude):
        raise NotImplementedError

    def read(self, fname, size):
        raise NotImplementedError

    def write(self, content, fname):
        raise NotImplementedError
