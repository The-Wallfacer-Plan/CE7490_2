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
    """
    This is the interface of RAID, it provides 3 basic operations: read, write, recover
    """

    def __init__(self, N):
        """
        :param N: the total number of disks available
        """
        # BYTE_TYPE
        self.BYTE_TYPE = config.BYTE_TYPE
        # padding value
        self.ZERO = config.ZERO
        # total disk number
        self.N = N
        # denoting the path of the RAID system
        self._disk_path = os.path.join(config.root, self.__class__.__name__)
        # initialize disk array
        utils.setup_disks(self._disk_path, self.N)

    def get_real_name(self, disk_index, fname):
        """
        get the real data name outside the RAID system
        :param disk_index: the index of the disk
        :param fname: fake file name used for position simulation
        """
        return os.path.join(self._disk_path, config.disk_prefix + str(disk_index), fname)

    def __read_impl(self, excluded, fpath):
        """
        single read operation, if excluded==True, return a empty list, otherwise return data content
        """
        if excluded:
            return list()
        return utils.read_content(fpath)

    def __is_excluded(self, i, exclude):
        """
        determine whether disk i should be excluded
        :param i:
        :param exclude: an int or a int list
        :return:
        """
        if (isinstance(exclude, int) and i == exclude) or (isinstance(exclude, list) and i in exclude):
            return True
        return False

    def _read_n(self, fname, N, exclude=None):
        """
        a concurrent read operation; if exclude present, don't read the corresponding disk
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
        # get_logger().info(content_list)
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # list of bytes (int) list
        byte_list = []
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.ZERO] * (length - len(content))
            byte_list.append(current_str_list)
        # bytes array
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        # get_logger().info(byte_nparray)
        return byte_nparray

    def _gen_ndarray_from_content(self, content, num):
        """
        convert the content into numpy 2-darray
        :param content: read content
        :param num: 1st dimension size
        :return:
        """
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
        """
        convert 1-darray to str for write
        """
        # TODO: determine whether filtering is actually needed
        real_write_content = filter(lambda b: b >= self.ZERO, _1darray)
        str_list = [chr(b) for b in real_write_content]
        return ''.join(str_list)

    def __write_impl(self, fpath, write_array):
        """
        single file write
        """
        content = self._1darray_to_str(write_array)
        utils.write_content(fpath, content)

    def _write_n(self, fname, write_array, N):
        """
        concurrent write, N is the number of disks; we also allow the max executor to be N
        """
        fpath_list = [self.get_real_name(i, fname) for i in range(N)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
            executor.map(self.__write_impl, fpath_list, write_array)

    def check(self, byte_ndarray):
        """
        integrity check; implemented by concrete RAID
        :param byte_ndarray: data type
        """
        raise NotImplementedError

    def recover(self, fname, exclude):
        """
        recover the "execlude" disk; implemented by concrete RAID
        :param fname: data name
        :param exclude: the excluded disk index (list) to be recovered
        :return:
        """
        raise NotImplementedError

    def read(self, fname, size):
        """
        read operation; implemented by concrete RAID
        :param fname: data name
        :param size: size of data chunk
        :return:
        """
        raise NotImplementedError

    def write(self, content, fname):
        """
        write operation; implemented by concrete RAID
        :param content: the raw content to be write
        :param fname: data name
        :return:
        """
        raise NotImplementedError
