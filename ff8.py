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
            get_logger().warning('{:0{width}{base}}'.format(g, base='x', width=2))


    @staticmethod
    def i2P(sInt):
        """Convert an integer into a polynomial"""
        return [(sInt >> i) & 1 for i in reversed(range(sInt.bit_length()))]


if __name__ == '__main__':
    init_logger()
    gf8 = GF()


#######################################

mask1 = mask2 = polyred = None


def setGF2(degree, irPoly):
    """Define parameters of binary finite field GF(2^m)/g(x)
       - degree: extension degree of binary field
       - irPoly: coefficients of irreducible polynomial g(x)
    """
    print('setGF2: n={}, F={:0{width}b}({})'.format(degree, irPoly, irPoly, width=degree + 1))

    def i2P(sInt):
        """Convert an integer into a polynomial"""
        return [(sInt >> i) & 1 for i in reversed(range(sInt.bit_length()))]

    global mask1, mask2, polyred
    mask1 = mask2 = 1 << degree
    mask2 -= 1
    polyred = reduce(lambda x, y: (x << 1) + y, i2P(irPoly)[1:])
    # print(polyred)


def addGF2(p1, p2):
    return p1 ^ p2


def subGF2(p1, p2):
    return p1 ^ p2


def multGF2(p1, p2):
    """Multiply two polynomials in GF(2^m)/g(x)"""
    p = 0
    while p2:
        if p2 & 1:
            p ^= p1
        p1 <<= 1
        if p1 & mask1:
            p1 ^= polyred
        p2 >>= 1
    return p & mask2


op_fn_dict = {
    'x': multGF2,
    '+': subGF2,
    '-': addGF2
}


def evaluate(p1, op, p2):
    fn = op_fn_dict[op]
    res = fn(p1, p2)
    print('{:0{width}b} {} {:0{width}b} = {:0{width}b}'.format(p1, op, p2, res, width=N + 1))


def run():
    global N
    N = 8
    F = 0b100011101
    setGF2(N, F)
    a = 0b000000010
    print(multGF2(a, a))
    evaluate(a, 'x', a)


if __name__ == '__main__':
    run()
