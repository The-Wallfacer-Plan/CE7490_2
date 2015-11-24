#!/usr/bin/env python
from __future__ import print_function

from BitVector import BitVector

from log_helper import get_logger, init_logger


# noinspection PyCallingNonCallable,PyAttributeOutsideInit,PyPep8Naming
class GF(object):
    """
    This is a general implementation for GF8; it utilizes the BitVector module;
    initially used by us, but finally deprecated due to performance issues.
    Note: in order to avoid re-computation, it applies "borg pattern".
    """
    __shared_state = {}

    def __init__(self, N=8, modulus=0b100011101):
        """
        :param N: GF^N field
        :param modulus: the modulus value
        :return:
        """
        self.__dict__ = self.__shared_state
        # 2^N in
        self.N = N
        # self.modulus = BitVector(bitstring='100011011')
        self.modulus = BitVector(intVal=modulus)
        # the circle, 255 in GF^8
        self.circle = 2 ** self.N - 1
        if 'generator' not in self.__dict__:
            self.init_generator()

    def multiply(self, first, second):
        """
        multiplication operation
        :param first: multiplier
        :param second: multiplier
        :return: BitVector result
        """
        assert type(second) in [int, BitVector]
        if isinstance(second, int):
            second = BitVector(intVal=second)
        return first.gf_multiply_modular(second, self.modulus, self.N)

    def log_generator(self, result):
        """
        log_g operation
        :param result: the value to be log
        :return: int result
        """
        get_logger().info(type(result))
        assert type(result) in (int, BitVector)
        if isinstance(result, BitVector):
            result = result.int_val()
        for i in range(self.circle):
            if self.generator[i].int_val() == result:
                return i

    def power(self, a, n):
        """
        compute a^n
        :param a:
        :param n:
        :return: BitVector result
        """
        n %= self.circle  # n is guaranteed >=0 after modular
        res = BitVector(intVal=1)
        if isinstance(a, BitVector):
            bv_a = a
        else:  # type(a) == int
            bv_a = BitVector(intVal=a)
        while True:
            if n == 0:
                return res
            n -= 1
            res = self.multiply(res, bv_a)

    def Axy(self, x, y):
        """
        The A_{xy} value used for two data disk recovery
        :param x: int
        :param y: int
        :return: BitVector result
        """
        g_y_sub_x = self.generator[(y - x) % self.circle]
        _base = g_y_sub_x ^ BitVector(intVal=1)
        second = self.power(_base, -1)
        return self.multiply(g_y_sub_x, second)

    def Bxy(self, x, y):
        """
        The B_{xy} value used for two data disk recovery
        :param x:
        :param y:
        :return: BitVector result
        """
        g_neg_x = self.generator[(-x) % self.circle]
        g_y_sub_x = self.generator[(y - x) % self.circle]
        _base = g_y_sub_x ^ BitVector(intVal=1)
        second = self.power(_base, -1)
        return self.multiply(g_neg_x, second)

    def init_generator(self):
        """
        pre-compute the lookup table of the generator
        """
        get_logger().info('init generator')
        self.generator = []
        res = BitVector(intVal=1)
        base = BitVector(intVal=2)
        counter = 0
        while True:
            self.generator.append(res)
            self.dump_bitvector(res)
            counter += 1
            if counter >= self.circle:
                break
            res = self.multiply(res, base)
        assert len(set(self.generator)) == self.circle

    @staticmethod
    def dump_bitvector(bv, display_base='x', display_width=2):
        """
        helper method to dump bitvector
        :param bv:
        :param display_base:
        :param display_width:
        :return:
        """
        int_val = int(str(bv), base=2)
        get_logger().info('{:0{width}{base}}'.format(int_val, base=display_base, width=display_width))


if __name__ == '__main__':
    init_logger()
    gf = GF()
    # for i, g in enumerate(gf.generator):
    #     print('{:3d} {:>s}'.format(i, g))
    a = 2
    print(gf.power(a, 255))
