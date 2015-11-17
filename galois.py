#!/usr/bin/env python
from __future__ import print_function

from BitVector import BitVector

from log_helper import get_logger, init_logger


# noinspection PyCallingNonCallable,PyAttributeOutsideInit
class GF(object):
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.N = 8
        # self.modulus = BitVector(bitstring='100011011')
        self.modulus = BitVector(bitstring='100011101')
        self.circle = 2 ** self.N - 1
        if 'generator' not in self.__dict__:
            self.init_generator()

    def multiply(self, first, second):
        return first.gf_multiply_modular(second, self.modulus, self.N)

    def power(self, a, n):
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
        g_y_sub_x = self.generator[(y - x) % self.circle]
        _base = g_y_sub_x ^ BitVector(intVal=1)
        second = self.power(_base, -1)
        return self.multiply(g_y_sub_x, second)

    def Bxy(self, x, y):
        g_neg_x = self.generator[(-x) % self.circle]
        g_y_sub_x = self.generator[(y - x) % self.circle]
        _base = g_y_sub_x ^ BitVector(intVal=1)
        second = self.power(_base, -1)
        return self.multiply(g_neg_x, second)

    def init_generator(self):
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
        intval = int(str(bv), base=2)
        get_logger().info('{:0{width}{base}}'.format(intval, base=display_base, width=display_width))


if __name__ == '__main__':
    init_logger()
    gf = GF()
    # for i, g in enumerate(gf.generator):
    #     print('{:3d} {:>s}'.format(i, g))
    a = 2
    print(gf.power(a, 255))
