import os
from itertools import repeat

import concurrent
import concurrent.futures
import numpy as np

import config
import utils
# noinspection PyPep8Naming
from log_helper import get_logger


# noinspection PyPep8Naming
class RAID(object):
    def __init__(self, N):
        """
        :param N: the total number of disks available
        """
        self.BYTE_TYPE = config.BYTE_TYPE
        self.ZERO = config.ZERO
        self.N = N
        self._disk_path = os.path.join(config.root, self.__class__.__name__)
        utils.setup_disks(self._disk_path, self.N)

    def get_real_name(self, disk_index, fname):
        """
        :param disk_index: the index of the disk
        :param fname: fake file name used for position simulation
        :return:
        """
        return os.path.join(self._disk_path, config.disk_prefix + str(disk_index), fname)

    def __read_impl(self, excluded, fpath):
        if excluded:
            return list()
        return utils.read_content(fpath)

    def __is_excluded(self, i, exclude):
        if (isinstance(exclude, int) and i == exclude) or (isinstance(exclude, list) and i in exclude):
            return True
        return False

    def _read_n(self, fname, N, exclude=None):
        """
        generate nparray with dtype=BYTE_TYPE
        :param fname:
        :return: ndarray with shape=(n, length)
        """
        excluded_list = [self.__is_excluded(i, exclude) for i in range(N)]
        fpath_list = [self.get_real_name(i, fname) for i in range(N)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
            content_list = list(executor.map(self.__read_impl, excluded_list, fpath_list))
        ######
        # content_list = []
        # for i in range(N):
        #     if (isinstance(exclude, int) and i == exclude) or (isinstance(exclude, list) and i in exclude):
        #         content_list.append(list())
        #     else:
        #         fpath = self.get_real_name(i, fname)
        #         content_list.append(utils.read_content(fpath))
        ######
        get_logger().info(content_list)
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # list of bytes (int) list
        byte_list = []
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.ZERO] * (length - len(content))
            byte_list.append(current_str_list)
        # bytes array
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        get_logger().info(byte_nparray)
        return byte_nparray

    def _gen_ndarray_from_content(self, content, num):
        # gen N-1 length empty list
        content_list = [[] for i in repeat(None, num)]
        for i in xrange(len(content)):
            mod_i = i % num
            content_list[mod_i].append(content[i])
        byte_list = []
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # fill 0
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.ZERO] * (length - len(content))
            byte_list.append(current_str_list)
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        get_logger().info('byte_array'.format(byte_nparray))
        return byte_nparray

    def _1darray_to_str(self, _1darray):
        # TODO: determine whether filtering is actually needed
        real_write_content = filter(lambda b: b >= self.ZERO, _1darray)
        str_list = [chr(b) for b in real_write_content]
        return ''.join(str_list)

    def __write_impl(self, fpath, write_array):
        content = self._1darray_to_str(write_array)
        utils.write_content(fpath, content)

    def _write_n(self, fname, write_array, N):
        fpath_list = [self.get_real_name(i, fname) for i in range(N)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
            executor.map(self.__write_impl, fpath_list, write_array)

    # def _write_n(self, fname, write_array, N):
    #     r"""
    #     doesn't care about trailing '\x0'
    #     :param fname:
    #     :param write_array:
    #     :return:
    #     """
    #     get_logger().info('write_array:\n{}'.format(write_array))
    #     # write N
    #     assert write_array.shape[0] == N
    #     for i in range(N):
    #         fpath_i = self.get_real_name(i, fname)
    #         content_i = self._1darray_to_str(write_array[i])
    #         utils.write_content(fpath_i, content_i)

    def check(self, byte_ndarray):
        raise NotImplementedError

    def recover(self, fname, exclude):
        raise NotImplementedError

    def read(self, fname, size):
        raise NotImplementedError

    def write(self, content, fname):
        raise NotImplementedError
