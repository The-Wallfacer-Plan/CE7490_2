#!/usr/bin/env python

import numpy as np

# noinspection PyPep8Naming
import utils
from log_helper import get_logger
from raid4 import RAID4


# noinspection PyAbstractClass,PyPep8Naming
class RAID5(RAID4):
    """
    _check and recover is same as RAID4
    """

    def get_parity_index(self, i):
        return (3 - i) % self.N

    def swap(self, byte_ndarray):
        get_logger().info('before\n{}'.format(byte_ndarray))
        for i in xrange(self.N - 1):
            j = self.get_parity_index(i)
            get_logger().info('{}, {}'.format(byte_ndarray[i][j], byte_ndarray[self.N - 1][j]))
            byte_ndarray[i][j], byte_ndarray[self.N - 1][j] = byte_ndarray[self.N - 1][j], byte_ndarray[i][j]
        get_logger().info('after\n{}'.format(byte_ndarray))
        return byte_ndarray

    def __init__(self, N):
        assert 3 <= N
        super(RAID5, self).__init__(N)

    def read(self, fname, size):
        byte_ndarray = self._read_n(fname, self.N)
        self.check(byte_ndarray)
        assert byte_ndarray.ndim == 2
        assert byte_ndarray.shape[0] == self.N
        swapped = self.swap(byte_ndarray)
        filtered_ndarray = swapped[:-1]
        flat_list = filtered_ndarray.ravel(1)[:size]
        flat_str_list = [chr(e) for e in flat_list]
        return ''.join(flat_str_list)

    def __gen_raid_array(self, byte_ndarray):
        assert byte_ndarray.ndim == 2
        assert byte_ndarray.shape[0] + 1 == self.N
        parity = utils.parity(byte_ndarray)
        gen_ndarray = np.concatenate([byte_ndarray, parity])
        write_ndarray = self.swap(gen_ndarray)
        return write_ndarray

    def write(self, content, fname):
        byte_ndarray = self._gen_ndarray_from_content(content, self.N - 1)
        write_array = self.__gen_raid_array(byte_ndarray)
        self._write_n(fname, write_array, self.N)


if __name__ == '__main__':
    utils.simple_test(RAID5)
