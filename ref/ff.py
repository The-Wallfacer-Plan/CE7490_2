#!/usr/bin/env python

from functools import reduce

# constants used in the multGF2 function
mask1 = mask2 = polyred = None


def setGF2(degree, irPoly):
    """Define parameters of binary finite field GF(2^m)/g(x)
       - degree: extension degree of binary field
       - irPoly: coefficients of irreducible polynomial g(x)
    """
    print('setGF2: n={}, F={:0{width}b}({})'.format(degree, irPoly, irPoly, width=N + 1))

    def i2P(sInt):
        """Convert an integer into a polynomial"""
        return [(sInt >> i) & 1 for i in reversed(range(sInt.bit_length()))]

    global mask1, mask2, polyred
    mask1 = mask2 = 1 << degree
    mask2 -= 1
    polyred = reduce(lambda x, y: (x << 1) + y, i2P(irPoly)[1:])


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


if __name__ == "__main__":

    N = 3
    F = 0b1011

    setGF2(N, F)

    a = 0b111
    b = 0b101
    evaluate(a, '+', b)
    evaluate(a, '-', b)
    evaluate(a, 'x', b)

    N = 8
    F = 0b100011011
    setGF2(N, F)

    a = 0b10000000
    b = 0b10000011
    evaluate(a, 'x', b)

    N = 8
    F = 0b100011101
    setGF2(N, F)

    a = 0b10101010
    b = 0b00000010
    evaluate(a, 'x', b)
