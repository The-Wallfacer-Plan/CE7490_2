#!/usr/bin/env python
from __future__ import print_function

import numpy as np
from BitVector.BitVector import BitVector

import utils
from gf8 import GF
from log_helper import init_logger, get_logger
from raid import RAID


# noinspection PyPep8Naming


class RAID6(RAID):
    _logger = get_logger()

    def __init__(self, N):
        assert 4 <= N
        super(RAID6, self).__init__(N)
        self.gf = GF()

    # noinspection PyMethodMayBeStatic
    def gf_1darray_add(self, A1, A2):
        """
        :param A1:
        :param A2:
        :return: 1darray
        """
        return (A1 ^ A2).ravel(1)

    def gf_a_multiply_list(self, a, l):
        """
        :param a: BitVector type
        :param l:
        :return: list of int
        """
        return [self.gf.multiply(BitVector(intVal=i), a).int_val() for i in l]

    def check(self, byte_ndarray):
        # check p
        data_p_ndarray = byte_ndarray[:-1]
        utils.check_data_p(data_p_ndarray)
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

    def _get_corrupted_data_disk(self, P_star, Q_star):
        p0 = BitVector(intVal=P_star[0][0])
        q0 = BitVector(intVal=Q_star[0][0])
        log_p0 = self.gf.log_generator(p0)
        log_q0 = self.gf.log_generator(q0)
        return (log_q0 - log_p0) % self.gf.circle

    def detect_corruption(self, fname):
        """
        single disk corruption detection
        :param fname:
        :return: corrupted disk index
        """
        # all disks, including P, Q
        byte_ndarray = self._read_n(fname, self.N)
        data_ndarray = byte_ndarray[:-2]
        self._logger.info("byte_ndarray=\n{}".format(byte_ndarray))
        P = byte_ndarray[-2:-1]
        self._logger.info("p={}".format(P))
        Q = byte_ndarray[-1]
        self._logger.info("Q={}".format(Q))
        P_prime = utils.gen_p(data_ndarray, ndim=2)
        self._logger.info("P_prime={}".format(P_prime))
        Q_prime = utils.gen_q(data_ndarray, ndim=2)
        self._logger.info("Q_prime={}".format(Q_prime))
        P_star = np.bitwise_xor(P, P_prime)
        Q_star = np.bitwise_xor(Q, Q_prime)
        P_nonzero = np.count_nonzero(P_star)
        Q_nonzero = np.count_nonzero(Q_star)
        if P_nonzero == 0 and Q_nonzero == 0:
            print("no corruption")
            return None
        elif P_nonzero == 0 and Q_nonzero != 0:
            print("Q corruption")
            return self.N - 1
        elif P_nonzero != 0 and Q_nonzero == 0:
            print("P corruption")
            return self.N - 2
        else:
            index = self._get_corrupted_data_disk(P_star, Q_star)
            print("data disk {} corruption".format(index))
            return index

    def recover_d_or_p(self, fname, index):
        """
        recover data drive or 'p' drive, simply using XOR
        :param fname:
        :param index:
        :return:
        """
        assert 0 <= index < self.N - 1
        byte_ndarray = self._read_n(fname, self.N - 1, exclude=index)
        parity = utils.gen_p(byte_ndarray, ndim=1)
        content = self._1darray_to_str(parity)
        fpath = self.get_real_name(index, fname)
        utils.write_content(fpath, content)
        # check data or p
        read_ndarray = self._read_n(fname, self.N - 1)
        utils.check_data_p(read_ndarray)

    def recover_q(self, fname):
        """
        recover 'q' drive, recompute; no need to check here
        :param fname:
        :return:
        """
        byte_ndarray = self._read_n(fname, self.N - 2)
        q_ndarray = utils.gen_q(byte_ndarray, ndim=2)
        assert q_ndarray.ndim == 2
        new_num = q_ndarray.shape[1]
        q_ndarray.shape = (new_num,)
        content = self._1darray_to_str(q_ndarray)
        fpath = self.get_real_name(self.N - 1, fname)
        utils.write_content(fpath, content)

    def recover_d_q(self, fname, index):
        """
        recover data/'p' drive (index) and 'q' drive: firstly using XOR to recover data drive, then recompute q
        :param fname:
        :param index:
        :return:
        """
        self.recover_d_or_p(fname, index)
        self.recover_q(fname)

    def recover_2d(self, fname, x, y):
        """
        recover data drives (x and y)
        :param fname:
        :param x:
        :param y:
        :return:
        """
        assert 0 <= x < self.N - 2
        assert 0 <= y < self.N - 2
        assert x != y
        byte_ndarray = self._read_n(fname, self.N, exclude=[x, y])
        DD = byte_ndarray[:-2]
        P = byte_ndarray[-2:-1]
        Q = byte_ndarray[-1:]
        # Pxy
        Pxy = utils.gen_p(DD, ndim=2)
        # Qxy
        Qxy = utils.gen_q(DD, ndim=2)
        # Axy, Bxy
        A = self.gf.Axy(x, y)
        B = self.gf.Bxy(x, y)
        # Dx
        first = self.gf_a_multiply_list(A, self.gf_1darray_add(P, Pxy))
        second = self.gf_a_multiply_list(B, self.gf_1darray_add(Q, Qxy))
        Dx = self.gf_1darray_add(np.array(first), np.array(second))
        Dx_content = self._1darray_to_str(Dx)
        x_fpath = self.get_real_name(x, fname)
        utils.write_content(x_fpath, Dx_content)
        # Dy
        Dy = self.gf_1darray_add(P ^ Pxy, Dx)
        Dy_content = self._1darray_to_str(Dy)
        y_fpath = self.get_real_name(y, fname)
        utils.write_content(y_fpath, Dy_content)

    def recover_d_p(self, fname, index):
        """
        recover data drive (index) and 'p' drive
        :param fname:
        :param index:
        :return:
        """
        assert 0 <= index < self.N - 2
        byte_ndarray = self._read_n(fname, self.N, exclude=index)
        DD = byte_ndarray[:-2]
        Q = byte_ndarray[-1:]
        # Dx
        Qx = utils.gen_q(DD, ndim=2)
        g_x_inv = self.gf.generator[self.gf.circle - index]
        ###
        _add_list = self.gf_1darray_add(Q, Qx)
        Dx_list = self.gf_a_multiply_list(g_x_inv, _add_list)
        ###
        Dx_content = ''.join(chr(i) for i in Dx_list)
        x_fpath = self.get_real_name(index, fname)
        utils.write_content(x_fpath, Dx_content)
        # p
        Dx = np.array(Dx_list, ndmin=2)
        assert Dx.shape[1] == byte_ndarray.shape[1]
        # update firstly
        DD[index] = Dx
        P = utils.gen_p(DD, ndim=1)
        assert P.shape[0] == byte_ndarray.shape[1]
        # do not need to update DD
        P_content = self._1darray_to_str(P)
        P_path = self.get_real_name(self.N - 2, fname)
        utils.write_content(P_path, P_content)

    def write(self, content, fname):
        byte_ndarray = self._gen_ndarray_from_content(content, self.N - 2)
        p_ndarray = utils.gen_p(byte_ndarray, ndim=2)
        q_ndarray = utils.gen_q(byte_ndarray, ndim=2)
        write_ndarray = np.concatenate([byte_ndarray, p_ndarray, q_ndarray])
        self._write_n(fname, write_ndarray, self.N)


if __name__ == '__main__':
    # utils.simple_test(RAID6, False)
    init_logger()
    r6 = RAID6(8)
    original_content = b'good_morning\x03_sir_yes\x01\x02'
    # original_content = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13'
    # data_fname = 'good.dat'
    data_fname = 'data1'
    # fpath = os.path.join(config.root, data_fname)
    # with open(fpath, 'rb') as fh:
    #     original_content = fh.read()
    # r6.write(original_content, data_fname)
    # error_index = 0
    # r6.recover_d_or_p(data_fname, error_index)
    # r6.recover_d_p(data_fname, 1)
    # r6.recover_2d(data_fname, 0, 1)
    # r6_content = r6.read(data_fname, len(original_content))
    # print(r6_content.__repr__())
    r6.detect_corruption(data_fname)
