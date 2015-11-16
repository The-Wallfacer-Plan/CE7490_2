#!/usr/bin/env python
from __future__ import print_function

import numpy as np

import utils
from log_helper import init_logger
from raid import RAID


# noinspection PyPep8Naming,PyAttributeOutsideInit
class RAID4(RAID):
    def __init__(self, N):
        super(RAID4, self).__init__(N)

    def _check(self, byte_nparray):
        res = np.bitwise_xor.reduce(byte_nparray)
        if np.count_nonzero(res) != 0:
            msg = 'xor of arrays not all zeros, res={}'.format(res)
            raise utils.ParityCheckError(msg)

    def read(self, fname, size):
        byte_nparray = self._read_n(fname)
        # check
        self._check(byte_nparray)
        # get N-1
        data_nparray = byte_nparray[:-1]
        flat_list = data_nparray.ravel(1)[:size]
        flat_str_list = [chr(e) for e in flat_list]
        return ''.join(flat_str_list)

    def recover(self, fname, index):
        assert 0 <= index < self.N
        byte_ndarray = self._read_n(fname, exclude=index)
        parity = np.bitwise_xor.reduce(byte_ndarray)
        assert parity.ndim == 1
        content = self._1darray_to_str(parity)
        fpath = self.get_real_name(index, fname)
        with open(fpath, 'wb') as fh:
            fh.write(content)
            # check
        read_ndarray = self._read_n(fname)
        self._check(read_ndarray)

    def write(self, content, fname):
        byte_nparray = self._gen_ndarray_from_content(content)
        # calculate parity and append
        parity = self._parity(byte_nparray)
        # parity = np.bitwise_xor.reduce(byte_nparray)
        # assert parity.ndim == 1
        # new_num = parity.shape[0]
        # parity.shape = (1, new_num)
        write_array = np.concatenate([byte_nparray, parity])
        self._write_n(fname, write_array)


if __name__ == '__main__':
    init_logger()
    r4 = RAID4(4)
    data_fname = 'good.dat'
    original_content = 'good_morning_sir'
    # original_content = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13'
    size = len(original_content)
    r4.write(original_content, data_fname)
    r4_content = r4.read(data_fname, size)
    print(r4_content.__repr__())
    assert r4_content == original_content
    error_index = 2
    r4.recover(data_fname, error_index)
