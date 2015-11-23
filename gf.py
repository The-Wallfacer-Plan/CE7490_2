#!/usr/bin/env python
from __future__ import print_function

from functools import reduce

# constants used in the multGF2 function
from log_helper import get_logger, init_logger


class GF(object):
    __shared_state = {}

    def __init__(self, N=8, modulus=0b100011101):
        self.__dict__ = self.__shared_state
        self.N = N
        self.modulus = modulus
        self.mask1 = 1 << self.N
        self.mask2 = self.mask1 - 1
        self.polyred = reduce(lambda x, y: (x << 1) + y, self.i2P(self.modulus)[1:])
        # print(self.polyred)
        self.circle = 2 ** self.N - 1
        if 'generator' not in self.__dict__:
            self.init_generator()

    def multiply(self, p1, p2):
        """Multiply two polynomials in GF(2^m)/g(x)"""
        p = 0
        while p2:
            if p2 & 1:
                p ^= p1
            p1 <<= 1
            if p1 & self.mask1:
                p1 ^= self.polyred
            p2 >>= 1
        return p & self.mask2

    def init_generator(self):
        self.generator = []
        counter = 0
        res = 1
        base = 2
        while True:
            self.generator.append(res)
            counter += 1
            if counter >= self.circle:
                break
            # print('{}: {} {}'.format(counter, res, base), end='\t')
            res = self.multiply(res, base)
        assert len(self.generator) == self.circle
        for g in self.generator:
            get_logger().info('{:0{width}{base}}'.format(g, base='x', width=2))

    def log_generator(self, result):
        assert isinstance(result, int)
        for i in range(self.circle):
            if self.generator[i] == result:
                return i

    def Axy(self, x, y):
        g_y_sub_x = self.generator[(y - x) % self.circle]
        _base = g_y_sub_x ^ 1
        second = self.power(_base, -1)
        return self.multiply(g_y_sub_x, second)

    def Bxy(self, x, y):
        g_neg_x = self.generator[(-x) % self.circle]
        g_y_sub_x = self.generator[(y - x) % self.circle]
        _base = g_y_sub_x ^ 1
        second = self.power(_base, -1)
        return self.multiply(g_neg_x, second)

    def power(self, a, n):
        n %= self.circle  # n is guaranteed >=0 after modular
        res = 1
        while True:
            if n == 0:
                return res
            n -= 1
            res = self.multiply(res, a)

    @staticmethod
    def i2P(sInt):
        """Convert an integer into a polynomial"""
        return [(sInt >> i) & 1 for i in reversed(range(sInt.bit_length()))]


if __name__ == '__main__':
    init_logger()
    gf8 = GF()
