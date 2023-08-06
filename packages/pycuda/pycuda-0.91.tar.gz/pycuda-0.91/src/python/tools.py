"""Miscallenous helper functionality."""

from __future__ import division

__copyright__ = "Copyright (C) 2008 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import pycuda.driver as cuda
import pycuda.gpuarray as gpuarray
from pycuda._driver import DeviceMemoryPool 
from pycuda._driver import bitlog2



class DebugMemoryPool(DeviceMemoryPool):
    def __init__(self):
        DeviceMemoryPool.__init__(self)
        self.last_free, _ = cuda.mem_get_info()

        from weakref import WeakKeyDictionary
        self.blocks = WeakKeyDictionary()

        from pytools.diskdict import DiskDict
        self.stacktrace_mnemonics = DiskDict("pycuda-stacktrace-mnemonics")

    def allocate(self, size):
        print "  Allocation of size %d occurring (mem: last_free:%d, free: %d, total:%d) (pool: held:%d, active:%d):" % (
                (size, self.last_free) 
                + cuda.mem_get_info()
                + (self.held_blocks, self.active_blocks))
        histogram = {}
        for bsize, descr in self.blocks.itervalues():
            histogram[bsize, descr] = histogram.get((bsize, descr), 0) + 1

        for (bsize, descr), count in histogram.iteritems():
            print "  %s (%d bytes): %dx" % (descr, bsize, count)

        from traceback import extract_stack
        stack = tuple(frm[2] for frm in extract_stack())

        raw_input("  [Enter]")
        result = DeviceMemoryPool.allocate(self, size)
        self.blocks[result] = size, self.describe(stack, size)
        self.last_free, _ = cuda.mem_get_info()
        return result

    def describe(self, stack, size):
        try:
            return self.stacktrace_mnemonics[stack, size]
        except KeyError:
            print size, stack
            while True:
                mnemonic = raw_input("Enter mnemonic or [Enter] for more info:")
                if mnemonic == '':
                    from traceback import print_stack
                    print_stack()
                else:
                    break
            self.stacktrace_mnemonics[stack, size] = mnemonic
            return mnemonic
        



def _exact_div(dividend, divisor):
    quot, rem = divmod(dividend, divisor)
    assert rem == 0
    return quot

def _int_ceiling(value, multiple_of=1):
    """Round C{value} up to be a C{multiple_of} something."""
    # Mimicks the Excel "floor" function (for code stolen from occupany calculator)

    from math import ceil
    return int(ceil(value/multiple_of))*multiple_of

def _int_floor(value, multiple_of=1):
    """Round C{value} down to be a C{multiple_of} something."""
    # Mimicks the Excel "floor" function (for code stolen from occupany calculator)

    from math import floor
    return int(floor(value/multiple_of))*multiple_of




def get_default_device(default=0):
    from pycuda.driver import Device
    import os
    dev = os.environ.get("CUDA_DEVICE")

    if dev is None:
        try:
            dev = (open(os.path.join(os.path.expanduser("~"), ".cuda_device"))
                    .read().strip())
        except:
            pass

    if dev is None:
        dev = default

    try:
        dev = int(dev)
    except TypeError:
        raise TypeError("CUDA device number (CUDA_DEVICE or ~/.cuda-device) must be an integer")
        
    return Device(dev)




class DeviceData:
    def __init__(self, dev=None):
        import pycuda.driver as drv

        if dev is None:
            dev = cuda.Context.get_device()

        self.max_threads = dev.get_attribute(drv.device_attribute.MAX_THREADS_PER_BLOCK)
        self.warp_size = dev.get_attribute(drv.device_attribute.WARP_SIZE)

        if dev.compute_capability() < (1,2):
            self.warps_per_mp = 24
        else:
            self.warps_per_mp = 32

        self.thread_blocks_per_mp = 8
        self.registers = dev.get_attribute(drv.device_attribute.MAX_REGISTERS_PER_BLOCK)
        self.shared_memory = dev.get_attribute(drv.device_attribute.MAX_SHARED_MEMORY_PER_BLOCK)

        self.smem_granularity = 16

    def align(self, bytes, word_size=4):
        return _int_ceiling(bytes, self.align_bytes(word_size))

    def align_dtype(self, elements, dtype_size):
        return _int_ceiling(elements, 
                self.align_words(dtype_size))

    def align_words(self, word_size):
        return _exact_div(self.align_bytes(word_size), word_size)

    def align_bytes(self, word_size=4):
        if word_size == 4:
            return 64
        elif word_size == 8:
            return 128
        elif word_size == 16:
            return 128
        else:
            raise ValueError, "no alignment possible for fetches of size %d" % word_size

    def coalesce(self, thread_count):
        return _int_ceiling(thread_count, 16)

    @staticmethod
    def make_valid_tex_channel_count(size):
        valid_sizes = [1,2,4]
        for vs in valid_sizes:
            if size <= vs:
                return vs

        raise ValueError, "could not enlarge argument to valid channel count"




class OccupancyRecord:
    def __init__(self, devdata, threads, shared_mem=0, registers=0):
        if threads > devdata.max_threads:
            raise ValueError("too many threads")

        # copied literally from occupancy calculator
        alloc_warps = _int_ceiling(threads/devdata.warp_size)
        alloc_regs = _int_ceiling(alloc_warps*2, 4)*16*registers
        alloc_smem = _int_ceiling(shared_mem, 512)

        if alloc_regs > devdata.registers:
            raise ValueError("too many registers")

        if alloc_smem > devdata.shared_memory:
            raise ValueError("too much smem")

        self.tb_per_mp_limits = [(devdata.thread_blocks_per_mp, "device"),
                (_int_floor(devdata.warps_per_mp/alloc_warps), "warps")
                ]
        if registers > 0:
            self.tb_per_mp_limits.append((_int_floor(devdata.registers/alloc_regs), "regs"))
        if shared_mem > 0:
            self.tb_per_mp_limits.append((_int_floor(devdata.shared_memory/alloc_smem), "smem"))

        self.tb_per_mp, self.limited_by = min(self.tb_per_mp_limits)

        self.warps_per_mp = self.tb_per_mp * alloc_warps
        self.occupancy = self.warps_per_mp / devdata.warps_per_mp




def allow_user_edit(s, filename, descr="the file"):
    from tempfile import mkdtemp
    tempdir = mkdtemp()

    from os.path import join
    full_name = join(tempdir, filename)

    outf = open(full_name, "w")
    outf.write(str(s))
    outf.close()

    raw_input("Edit %s at %s now, then hit [Enter]:" 
            % (descr, full_name))

    inf = open(full_name, "r")
    result = inf.read()
    inf.close()

    return result




def _test_occupancy():
    for threads in range(32, 512, 16):
        for smem in range(1024, 16384+1, 1024):
            occ = Occupancy(threads, smem)
            print "t%d s%d: %f %s" % (threads, smem, occ.occupancy, occ.limited_by)




if __name__ == "__main__":
    import pycuda.driver as drv
    drv.init()

    _test_occupancy()
