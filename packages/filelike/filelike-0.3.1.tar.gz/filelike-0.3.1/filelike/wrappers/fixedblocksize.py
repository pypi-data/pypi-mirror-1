# filelike/wrappers/fixedblocksize.py
#
# Copyright (C) 2006-2008, Ryan Kelly
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
"""

    filelike.wrappers.fixedblocksize:  read/write only on block boundaries
    
This module provides the filelike wrapper 'FixedBlockSize' to ensure that
reads/writes to the underlying file are only performed at block boundaries.

""" 

import filelike
from filelike.wrappers import FileWrapper

import unittest
from StringIO import StringIO


class FixedBlockSize(FileWrapper):
    """Class reading/writing to files at a fixed block size.
    
    This file wrapper can be used to read or write to a file-like
    object at a specific block size.  All reads request strings
    whose length is a multiple of the block size, and all writes
    pass on strings of a similar nature.  This could be useful, for
    example, to write data to a cipher function without manually 
    chunking text to match the cipher's block size.
    
    No padding is added to the file is its length is not a multiple 
    of the blocksize.
    """
    
    def __init__(self,fileobj,blocksize,mode=None):
        super(FixedBlockSize,self).__init__(fileobj,mode)
        self.blocksize = blocksize
    
    def _round_up(self,num):
        """Round <num> up to a multiple of the block size."""
        if num % self.blocksize == 0:
            return num
        return ((num/self.blocksize)+1) * self.blocksize
    
    def _round_down(self,num):
        """Round <num> down to a multiple of the block size."""
        if num % self.blocksize == 0:
            return num
        return (num/self.blocksize) * self.blocksize

    def _read(self,sizehint=-1):
        """Read approximately <sizehint> bytes from the file."""
        if sizehint >= 0:
            sizehint = self._round_up(sizehint)
        data = self._fileobj.read(sizehint)
        if data == "":
            return None
        return data

    def _write(self,data,flushing=False):
        """Write the given string to the file.

        When flushing data to the file, it may need to be padded to the
        block size.  We attempt to read additional data from the
        underlying file to use for the padding.
        """
        size = self._round_down(len(data))
        self._fileobj.write(data[:size])
        if len(data) == size:
            return ""
        if not flushing:
            return data[size:]
        # Flushing, so we need to try to pad the data with existing contents.
        # If we can't find such contents, just write at non-blocksize.
        if self._check_mode("r"):
            nextBlock = self._fileobj.read(self.blocksize)
            self._fileobj.seek(-1*len(nextBlock),1)
        else:
            nextBlock = ""
        padstart = len(data) - size
        self._fileobj.write(data[size:] + nextBlock[padstart:])
        # Seek back to start of previous block, if the file is readable.
        if self._check_mode("r"):
            self.seek(padstart - self.blocksize,1)
        return ""

    # TODO: primative implementation of relative seek
    def _seek(self,offset,whence):
        """Absolute seek, repecting block boundaries.

        This method performs an absolute file seek to the block boundary
        closest to (but not exceeding) the specified offset.
        """
        if whence != 0:
            raise NotImplementedError
        boundary = self._round_down(offset)
        self._fileobj.seek(boundary,0)
        if boundary == offset:
            return ""
        else:
            data = self._fileobj.read(self.blocksize)
            diff = offset - boundary - len(data)
            if diff > 0:
                # Seeked past end of file.  Actually do this on fileobj, so
                # that it will raise an error if appropriate.
                self._fileobj.seek(diff,1)
                self._fileobj.seek(-1*diff,1)
            self._fileobj.seek(-1*len(data),1)
            return data[:(offset-boundary)]
 

class Test_FixedBlockSize5(filelike.Test_ReadWriteSeek):
    """Testcases for the FixedBlockSize class, with blocksize 5."""

    blocksize = 5
    
    def makeFile(self,contents,mode):
        f = StringIO(contents)
        f.seek(0)
        class BSFile:
            """Simulate reads/writes, asserting correct blocksize."""
            def read(s,size=-1):
                self.assert_(size < 0 or size % self.blocksize == 0)
                return f.read(size)
            def write(s,data):
                self.assert_(len(data)%self.blocksize == 0)
                f.write(data)
            def seek(s,offset,whence):
                f.seek(offset,whence)
            def tell(s):
                return f.tell()
            def flush(self):
                f.flush()
        return FixedBlockSize(BSFile(),self.blocksize)


class Test_FixedBlockSize7(Test_FixedBlockSize5):
    """Testcases for the FixedBlockSize class, with blocksize 7."""
    blocksize = 7


class Test_FixedBlockSize24(Test_FixedBlockSize5):
    """Testcases for the FixedBlockSize class, with blocksize 24."""
    blocksize = 24


def testsuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_FixedBlockSize5))
    suite.addTest(unittest.makeSuite(Test_FixedBlockSize7))
    suite.addTest(unittest.makeSuite(Test_FixedBlockSize24))
    return suite

