#!/usr/bin/env python
from __future__ import print_function

import BitVector

from log_helper import get_logger, init_logger


# noinspection PyCallingNonCallable,PyAttributeOutsideInit
class GF(object):
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.N = 8
        self.modulus = BitVector.BitVector(bitstring='100011011')
        self.circle = 2 ** self.N - 1
        if 'generator' not in self.__dict__:
            self.init_generator()

    def init_generator(self):
        get_logger().info('init generator')
        self.generator = []
        res = BitVector.BitVector(intVal=1)
        base = BitVector.BitVector(intVal=2)
        counter = 0
        while True:
            self.generator.append(res)
            self.dump_bitvector(res)
            counter += 1
            if counter >= self.circle:
                break
            res = res.gf_multiply_modular(base, self.modulus, self.N)
        print(len(self.generator))

    @staticmethod
    def dump_bitvector(bv, display_base='x', display_width=2):
        intval = int(str(bv), base=2)
        get_logger().info('{:0{width}{base}}'.format(intval, base=display_base, width=display_width))


if __name__ == '__main__':
    init_logger()
    gf = GF()
