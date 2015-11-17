#!/usr/bin/env python
from raid import RAID


# noinspection PyPep8Naming


class RAID6(RAID):
    def __init__(self, N):
        assert 4 <= N
        super(RAID6, self).__init__(N)

    def _check(self, byte_nparray):
        pass

    def read(self, fname, size):
        byte_ndarray = self._read_n(fname)
        self._check(byte_ndarray)
        data_ndarray = byte_ndarray[:-2]
        flat_list = data_ndarray.ravel(1)[:size]
        flat_str_list = [chr(e) for e in flat_list]
        return ''.join(flat_str_list)

    def recover_d(self, fname, index):
        """
        recover data drive or 'p' drive, simply using XOR
        :param fname:
        :param index:
        :return:
        """
        pass

    def recover_q(self, fname):
        """
        recover 'q' drive, recompute
        :param fname:
        :return:
        """
        pass

    def recover_d_q(self, fname, index):
        """
        recover data drive (index) and 'q' drive: firstly using XOR to recover data drive, then recompute q
        :param fname:
        :param index:
        :return:
        """
        pass

    def recover_d_p(self, fname, index):
        """
        recover data drive (index) and 'p' drive
        :param fname:
        :param index:
        :return:
        """

    def recover_2d(self, fname, i1, i2):
        """
        recover data drives (i1 and i2)
        :param fname:
        :param i1:
        :param i2:
        :return:
        """

    def write(self, content, fname):
        pass
