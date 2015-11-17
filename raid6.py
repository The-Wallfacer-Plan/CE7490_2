#!/usr/bin/env python
import numpy as np

import utils
from raid import RAID


# noinspection PyPep8Naming


class RAID6(RAID):
    def __init__(self, N):
        assert 4 <= N
        super(RAID6, self).__init__(N)

    def check(self, byte_ndarray):
        # check p
        data_p_ndarray = byte_ndarray[:-1]
        utils.check_p(data_p_ndarray)
        # check_q
        data_ndarray = byte_ndarray[:-2]
        q_ndarray = byte_ndarray[-1:]
        utils.check_q(data_ndarray, q_ndarray)

    def read(self, fname, size):
        byte_ndarray = self._read_n(fname, self.N)
        self.check(byte_ndarray)
        data_ndarray = byte_ndarray[:-2]
        flat_list = data_ndarray.ravel(1)[:size]
        flat_str_list = [chr(e) for e in flat_list]
        return ''.join(flat_str_list)

    def recover(self, fname, exclude):
        raise NotImplementedError("not implemented; split into several cases")

    def recover_d_or_p(self, fname, index):
        """
        recover data drive or 'p' drive, simply using XOR
        :param fname:
        :param index:
        :return:
        """
        assert 0 <= index < self.N - 1
        byte_ndarray = self._read_n(fname, self.N - 1, exclude=index)
        parity = np.bitwise_xor.reduce(byte_ndarray)
        assert parity.ndim == 1
        content = self._1darray_to_str(parity)
        fpath = self.get_real_name(index, fname)
        with open(fpath, 'wb') as fh:
            fh.write(content)
        # check data or p
        read_ndarray = self._read_n(fname, self.N - 1)
        utils.check_p(read_ndarray)

    def recover_d_q(self, fname, index):
        """
        recover data/'p' drive (index) and 'q' drive: firstly using XOR to recover data drive, then recompute q
        :param fname:
        :param index:
        :return:
        """
        self.recover_d_or_p(fname, index)
        self.recover_q(fname)

    def recover_d_p(self, fname, index):
        """
        recover data drive (index) and 'p' drive
        :param fname:
        :param index:
        :return:
        """

    def recover_q(self, fname):
        """
        recover 'q' drive, recompute
        :param fname:
        :return:
        """
        pass

    def recover_2d(self, fname, i1, i2):
        """
        recover data drives (i1 and i2)
        :param fname:
        :param i1:
        :param i2:
        :return:
        """

    def write(self, content, fname):
        byte_ndarray = self._gen_ndarray_from_content(content, self.N - 2)
        p_ndarray = utils.parity(byte_ndarray)
        q_ndarray = utils.gf(byte_ndarray)
        write_ndarray = np.concatenate([byte_ndarray, p_ndarray, q_ndarray])
        self._write_n(fname, write_ndarray, self.N)


if __name__ == '__main__':
    utils.test_once(RAID6, False)
