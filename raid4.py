#!/usr/bin/env python
from __future__ import print_function

import numpy as np

import utils
from log_helper import get_logger
from raid import RAID


# noinspection PyPep8Naming,PyAttributeOutsideInit
class RAID4(RAID):
    def __init__(self, N):
        super(RAID4, self).__init__(N)

    def check(self, byte_ndarray):
        utils.check_data_p(byte_ndarray)

    def read(self, fname, size):
        byte_ndarray = self._read_n(fname, self.N)
        # check
        self.check(byte_ndarray)
        # get N-1
        data_nparray = byte_ndarray[:-1]
        flat_list = data_nparray.ravel(1)[:size]
        flat_str_list = [chr(e) for e in flat_list]
        return ''.join(flat_str_list)

    def recover(self, fname, index):
        assert 0 <= index < self.N
        byte_ndarray = self._read_n(fname, self.N, exclude=index)
        parity = np.bitwise_xor.reduce(byte_ndarray)
        assert parity.ndim == 1
        content = self._1darray_to_str(parity)
        fpath = self.get_real_name(index, fname)
        utils.write_content(fpath, content)
        # check
        read_ndarray = self._read_n(fname, self.N)
        self.check(read_ndarray)

    def __gen_raid_array(self, byte_ndarray):
        # calculate parity and append
        parity = utils.gen_p(byte_ndarray)
        write_array = np.concatenate([byte_ndarray, parity])
        get_logger().info('write_array=\n{}'.format(write_array))
        return write_array

    def write(self, content, fname):
        byte_ndarray = self._gen_ndarray_from_content(content, self.N - 1)
        write_array = self.__gen_raid_array(byte_ndarray)
        self._write_n(fname, write_array, self.N)


if __name__ == '__main__':
    utils.simple_test(RAID4)
