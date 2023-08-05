# filelike.py
#
# Copyright (C) 2006, Ryan Kelly
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
The filelike module takes care of the groundwork for implementing and
handling file-like objects that implement a rich file-like interface,
including reading, writing, and iteration.  It also provides a number
of useful classes built on top of this functionality.

The main class is FileLikeBase, which implements the entire file-like
interface (currently minus seek() and tell()) on top of primitive
_read() and _write() methods.  Subclasses may implement either or
both of these methods to obtain all the higher-level file behaviors.

On top of this framework are built a collection of useful classes,
including:
    
    * TransFile:  pass file contents through an arbitrary translation
                  function (e.g. compression, encryption, ...)
                  
    * FixedBlockSizeFile:  ensure all read/write requests are aligned with
                           a given blocksize
                           
    * DecryptFile:    on-the-fly reading and writing to an encrypted file
                      (using PEP272 cipher API)
                     
 
As an example of the type of thing this module is designed to achieve, here's
an example of using the DecryptFile class to transparently access an encrypted
file:
    
    # Create the decryption key
    from Crypto.Cipher import DES
    cipher = DES.new('abcdefgh',DES.MODE_ECB)
    # Open the encrypted file
    f = DecryptFile(file("some_encrypted_file.bin","r"),cipher)
    
The object in <f> now behaves as a file-like object, transparently decrypting
the file on-the-fly as it is read.
    
""" 

__ver_major__ = 0
__ver_minor__ = 1
__ver_patch__ = 0
__ver_sub__ = ""
__version__ = "%d.%d.%d%s" % (__ver_major__,__ver_minor__,
                              __ver_patch__,__ver_sub__)



import unittest


class FileLikeBase:
    """Base class for implementing file-like objects.
    
    This class takes a lot of the legwork out of writing file-like objects
    with a rich interface.  It implements the higher-level file-like
    methods on top of primitive _read() and _write() methods. See their
    docstrings for precise details on how they should behave.
    Subclasses then need only implement one or both of these methods for
    full file-like interface compatability.  They may of course override
    other methods as desired.

    NOTE: this class currently does not support seek() or tell().  It could
          probably be added if needed, but might be very slow...
  
    The class is missing the following attributes, which dont really make
    sense for anything but real files:
        
        * fileno()
        * isatty()
        * truncate()
        * encoding
        * mode
        * name
        * newlines
        
    Also unlike standard file objects, all read methods share the same
    buffer and so can be freely mixed (e.g. read(), readling(), next(), ...)
    
    """
    
    def __init__(self,lookahead=100):
        """FileLikeBase Constructor.
        The optional argument <lookahead> specifies the number of bytes to
        read at a time when looking a newline character.  Setting this to
        a larger number when lines are long should improve efficiency.
        """
        # File attributes
        self.closed = False
        self.softspace = 0
        # Our own attributes
        self.__lookahead = lookahead
        self.__buffer = ""
    
    def seek(self,offset,whence=0):
        """Provided for compatability only - FileLikeBase is not seekable."""
        raise IOError("Object not seekable")
    
    def tell(self):
        """Provided for compatability only - FileLikeBase is not seekable."""
        raise IOError("Object not seekable")
    
    def flush(self):
        """Flush internal write buffer, if necessary."""
        if self.closed:
            raise IOError("File has been closed")
    
    def __del__(self):
        self.close()
    
    def close(self):
        """Flush write buffers and close the file.
        The file may not be accessed further once it is closed.
        """
        if not self.closed:
            self.flush()
            self.closed = True
    
    def next(self):
        """next() method complying with the iterator protocol.
        File-like objects are their own iterators, with each call to
        next() returning subsequent lines from the file.
        """
        ln = self.readline()
        if ln == "":
            raise StopIteration()
        return ln
    
    def __iter__(self):
        return self
    
    def read(self,size=-1):
        """Read at most <size> bytes from the file.
        Bytes are returned as a string.  If <size> is negative, zero or
        missing, the remainder of the file is read.  If EOF is encountered
        immediately, the empty string is returned.
        """
        if self.closed:
            raise IOError("File has been closed")
        # Should the entire file be read?
        if size <= 0:
            data = [self.__buffer]
            self.__buffer = ""
            newData = self._read()
            while newData is not None:
                data.append(newData)
                newData = self._read()
            return "".join(data)
        # Want to return a specific amount of data
        data = []
        sizeSoFar = 0
        newData = self.__buffer
        while sizeSoFar < size and newData is not None:
            data.append(newData)
            sizeSoFar += len(newData)
            newData = self._read(size-sizeSoFar)
        data = "".join(data)
        if sizeSoFar > size:
            # read too many bytes, store in the buffer
            self.__buffer = data[size:]
            data = data[:size]
        else:
            self.__buffer = ""
        return data
        
    def readline(self,size=-1):
        """Read a line from the file, or a most <size> bytes."""
        bits = []
        indx = -1
        sizeSoFar = 0
        while indx == -1:
            nextBit = self.read(self.__lookahead)
            bits.append(nextBit)
            sizeSoFar += len(nextBit)
            if nextBit == "":
                break
            if size > 0 and sizeSoFar >= size:
                break
            indx = nextBit.find("\n")
        # If not found, return whole string up to <size> length
        # Any leftovers are pushed onto front of buffer
        if indx == -1:
            data = "".join(bits)
            if size > 0 and sizeSoFar > size:
                extra = data[size:]
                data = data[:size]
                self.__buffer = extra + self.__buffer
            return data
        # If found, push leftovers onto front of buffer
        # Add one to preserve the newline in the return value
        indx += 1
        extra = bits[-1][indx:]
        bits[-1] = bits[-1][:indx]
        self.__buffer = extra + self.__buffer
        return "".join(bits)
    
    def readlines(self,sizehint=-1):
        """Returna list of all lines in the file."""
        return [ln for ln in self]
    
    def xreadlines(self):
        """Iterator over lines in the file - equivalent to iter(self)."""
        return iter(self)

    def write(self,string):
        """Write the given string to the file."""
        if self.closed:
            raise IOError("File has been closed")    
        self._write(string)
    
    def writelines(self,seq):
        """Write a sequence of lines to the file."""
        for ln in seq:
            self.write(ln)
    
    def _read(self,sizehint=-1):
        """Read approximately <sizehint> bytes from the file-like object.
        
        This method is to be implemented by subclasses that wish to be
        readable.  It should read approximately <sizehint> bytes from the
        file and return them as a string.  If <sizehint> is missing or
        less than or equal to zero, try to read all the remaining contents.
        
        The method need not guarantee any particular number of bytes -
        it may return more bytes than requested, or fewer.  If needed, the
        size hint may be completely ignored.  It may even return an empty
        string if no data is yet available.
        
        Because of this, the method must return None to signify that EOF
        has been reached.  The higher-level methods will never indicate EOF
        until None has been read from _read().  Once EOF is reached, it
        should be safe to call _read() again, immediately returning None.
        
        TODO: should we guarantee that EOF will only be reached once, and
              cache this result at a higher level?
        """
        raise IOError("Object not readable")
    
    def _write(self,string):
        """Write the given string to the file-like object.
        
        This method must be implemented by subclasses wishing to be writable.
        It must behave as the standard write() method for file objects,
        simply writing the given string to the file.

        TODO: perhaps this could return the number of bytes successfully
              written, and any leftovers kept in a write buffer to try
              again when write() is next called?
        """
        raise IOError("Object not writable")



class FileWrapper(FileLikeBase):
    """Base class for objects that wrap a file-like object.
    
    This class provides basic functionality for implementing file-like
    objects that wrap another file-like object to alter its functionality
    in some way.  It takes care of house-keeping duties such as flushing
    and closing the wrapped file.

    Access to the wrapped file is given by the private member _fileobj.
    By convention, the subclass's constructor should accept this as its
    first argument and pass it to its superclass's constructor in the
    same position.
    
    This class provides a basic implementation of _read() and _write()
    which just calls read() and write() on the wrapped object.  Many
    subclasses will probably want to override these.
    """
    
    def __init__(self,fileobj):
        """FileWrapper constructor.
        
        <fileobj> must be a file-like object, which is to be wrapped
        in another file-like object to provide additional functionality.
        """
        FileLikeBase.__init__(self)
        self._fileobj = fileobj
        
    def close(self):
        """Close the object for reading/writing."""
        FileLikeBase.close(self)
        if hasattr(self._fileobj,"close"):
            self._fileobj.close()

    def flush(self):
        """Flush the write buffers of the file."""
        FileLikeBase.flush(self)
        if hasattr(self._fileobj,"flush"):
            self._fileobj.flush()
    
    def _read(self,sizehint=-1):
        data = self._fileobj.read(sizehint)
        if data == "":
            return None
        return data

    def _write(self,string):
        return self._fileobj.write(string)


class TransFile(FileWrapper):
    """Class implementing some translation on a file's contents.
    
    This class wraps a file-like object in another file-like object,
    applying a given function to translate the file's contents as it is
    read or written.  It could be used, for example, to read from a 
    gzipped source file or to encrypt a file as it's being written.
    
    The translating function must accept a string as its only argument,
    and return a transformed string representing the updated file contents.
    No guarantees are made about the amount of data fed into the function
    at a time (although another wrapper like FixedBlockSizeFile could be
    used to do so.)  If the transform needs to be flushed when reading/writing
    is finished, it should provide a flush() method that returns either None,
    or any data remaining to be read/written.
    
    Objects of this class support the standard sequential read/write
    interface if the object they are given does.  They do *not* support
    seeking or other forms of random access.
    """
    
    def __init__(self,fileobj,func,mode,size=None):
        """TransFile constructor.
        <fileobj> must be the file-like object whose contents are to be
        transformed, and <func> the callable that will transform the
        contents.  <mode> should be one of "r" or "w" to indicate whether
        reading or writing is desired.  If omitted it is determined from
        <fileobj> where possible, otherwise it defaults to "r".
        If <size> is given, it specifies the size of the
        transformed file.  Any extraneous data from <fileobj> will
        be discarded.
        """
        FileWrapper.__init__(self,fileobj)
        self._func = func
        if mode is None:
            if hasattr(fileobj,"mode"):
                if "w" in fileobj.mode:
                    mode = "w"
                else:
                    mode = "r"
            else:
                mode = "r"
        self.mode = mode
        self._size = size
        self._sizeSoFar = 0   # size of data read *and returned* so far
        self._finished = False
        # Copy useful attributes of the fileobj
        if hasattr(fileobj,"name"):
            self.name = fileobj.name
    
    def _flush_func(self):
        """Call flush on the translation function, if necessary."""
        if hasattr(self._func,"flush"):
            return self._func.flush()
        return None

    def _read(self,sizehint=-1):
        """Read approximately <sizehint> bytes from the file."""
        if self._finished:
            return None
        if sizehint <= 0:
            sizehint = 100
        data = self._fileobj.read(sizehint)
        if data == "":
            self._finished = True
            # Flush func if necessary
            data = self._flush_func()
            return data
        data = self._func(data)
        return data
    
    def _write(self,data):
        """Write the given data to the file."""
        self._fileobj.write(self._func(data))

    def flush(self):
        # Flush func if necessary, when writing
        if self.mode == "w":
            data = self._flush_func()
            if data is not None:
                self._fileobj.write(data)
        FileWrapper.flush(self)



class Test_TransFile(unittest.TestCase):
    """Testcases for the TransFile class."""
    
    def setUp(self):
        import StringIO
        self.testlines = ["this is a simple test\n"," file with a\n"," few lines."]
        self.testfileR = StringIO.StringIO("".join(self.testlines))
        self.testfileW = StringIO.StringIO()
        def noop(string):
            return string
        self.f_noop = noop
    
    def tearDown(self):
        del self.testfileR
        del self.testfileW

    def test_read(self):
        """Test reading the entire file"""
        tf = TransFile(self.testfileR,self.f_noop,"r")
        self.assert_(tf.read() == "".join(self.testlines))

    def test_readbytes(self):
        """Test reading a specific number of bytes"""
        tf = TransFile(self.testfileR,self.f_noop,"r")
        self.assert_(tf.read(10) == "".join(self.testlines)[:10])
        
    def test_readlines(self):
        """Test reading lines one at a time."""
        tf = TransFile(self.testfileR,self.f_noop,"r")
        self.assert_(tf.readlines() == self.testlines)
    
    def test_write(self):
        """Test basic behavior of writing to a file."""
        tf = TransFile(self.testfileW,self.f_noop,"w")
        tf.write("".join(self.testlines))
        self.assert_(self.testfileW.getvalue() == "".join(self.testlines))
    
    def test_writelines(self):
        """Test writing several lines with writelines()."""
        tf = TransFile(self.testfileW,self.f_noop,"w")
        tf.writelines(self.testlines)
        self.assert_(self.testfileW.getvalue() == "".join(self.testlines))
        

class FixedBlockSizeFile(FileWrapper):
    """Class reading/writing to files at a fixed block size.
    
    This file wrapper can be used to read or write to a file-like
    object at a specific block size.  All reads request strings
    whose length is a multiple of the block size, and all writes
    pass on strings of a similar nature.  This could be useful, for
    example, to write data to a cipher function without manually 
    chunking text to match cipher's block size.
    
    If the total data written to the file when it is flushed or closed
    is not a multiple of the blocksize, it will be padded with null
    bytes to the appropriate size.
    """
    
    def __init__(self,fileobj,blocksize):
        FileWrapper.__init__(self,fileobj)
        self._blocksize = blocksize
        self.__writebuffer = ""
    
    def _round_up(self,num):
        """Round <num> up to a multiple of the block size."""
        return ((num/self._blocksize)+1) * self._blocksize
    
    def _round_down(self,num):
        """Round <num> down to a multiple of the block size."""
        return (num/self._blocksize) * self._blocksize
    
    def _pad_to_size(self,data):
        """Add null bytes to data to make it an appropriate size."""
        size = self._round_up(len(data))
        if len(data) < size:
            data = data + ("\0"*(size-len(data)))
        return data
    
    def _read(self,sizehint=-1):
        """Read approximately <sizehint> bytes from the file."""
        if sizehint <= 0:
            sizehint = 100
        size = self._round_up(sizehint)
        data = self._fileobj.read(size)
        if data == "":
            return None
        return data

    def _write(self,string):
        """Write the given string to the file."""
        # Always round down to a mulitple of the blocksize
        data = self.__writebuffer + string
        size = self._round_down(len(data))
        self._fileobj.write(data[:size])
        self.__writebuffer = data[size:]
        
    def flush(self):
        """Flush internal write buffers."""
        data = self.__writebuffer
        if data != "":
            data = self._pad_to_size(data)
            self._fileobj.write(data)
        FileWrapper.flush(self)



class Test_FixedBlockSizeFile(unittest.TestCase):
    """Testcases for the FixedBlockSize class."""
    
    def setUp(self):
        import StringIO
        class BSFile:
            def __init__(s,bs):
                s.bs = bs
            def read(s,size=-1):
                self.assert_(size > 0)
                self.assert_(size%s.bs == 0)
                return "X"*size
            def write(s,data):
                self.assert_(len(data)%s.bs == 0)
        self.BSFile = BSFile
    
    def tearDown(self):
        del self.BSFile

    def test_readbytes(self):
        """Test reading different numbers of bytes"""
        bsf = FixedBlockSizeFile(self.BSFile(8),8)
        self.assert_(len(bsf.read(5)) == 5)
        self.assert_(len(bsf.read(8)) == 8)
        self.assert_(len(bsf.read(76)) == 76)
        bsf = FixedBlockSizeFile(self.BSFile(5),5)
        self.assert_(len(bsf.read(5)) == 5)
        self.assert_(len(bsf.read(8)) == 8)
        self.assert_(len(bsf.read(76)) == 76)
            
    def test_write(self):
        """Test writing different numbers of bytes"""
        bsf = FixedBlockSizeFile(self.BSFile(8),8)
        bsf.write("this is some text, it is")
        bsf.write("shrt")
        bsf.flush()
        bsf.write("longer text, with some\n newlines in it\n yessir.")   
        bsf.close() 


class DecryptFile(FileWrapper):
    """Class for reading and writing to an encrypted file.
    
    This class accesses an encrypted file using a ciphering object
    compliant with PEP272: "API for Block Encryption Algorithms".
    All reads from the file are automatically decrypted, while writes
    to the file and automatically encrypted.  Thus, DecryptFile(fobj)
    can be seen as the decrypted version of the file-like object fobj.
    
    Because this class is implemented on top of FixedBlockSizeFile,
    the plaintext may be padded with null characters to reach a multiple
    of the block size.
    
    There is a dual class, EncryptFile, where all reads are encrypted
    and all writes are decrypted.  This would be used, for example, to
    encrypt the contents of an existing file using a series of read()
    operations.
    """

    def __init__(self,fileobj,cipher,mode=None):
        """DecryptFile Constructor.
        <fileobj> is the file object with encrypted contents, and <cipher>
        is the cipher object to be used.  <mode> must be one of "r" or "w"
        to specify whether reading or writing is desired.  If omitted, the
        mode of <fileobj> is used if possible.  Otherwise, "r" is assumed.
        """
        self.__cipher = cipher
        myFileObj = TransFile(fileobj,self.__crypt,mode)
        self.mode = myFileObj.mode
        myFileObj = FixedBlockSizeFile(myFileObj,cipher.block_size)
        FileWrapper.__init__(self,myFileObj)
    
    def __crypt(self,data):
        """Encrypt/decrypt the given data depending on file mode.
        If mode is "r" then the data is decrypted.  Otherwise, it is
        encrypted.
        """
        if self.mode == "r":
            return self.__cipher.decrypt(data)
        return self.__cipher.encrypt(data)


class EncryptFile(FileWrapper):
    """Class for reading and writing to an decrypted file.
    
    This class accesses a decrypted file using a ciphering object
    compliant with PEP272: "API for Block Encryption Algorithms".
    All reads from the file are automatically encrypted, while writes
    to the file are automatically decrypted.  Thus, DecryptFile(fobj)
    can be seen as the encrypted version of the file-like object fobj.

    Because this class is implemented on top of FixedBlockSizeFile,
    the plaintext may be padded with null characters to reach a multiple
    of the block size.
    
    There is a dual class, DecryptFile, where all reads are decrypted
    and all writes are encrypted.  This would be used, for example, to
    decrypt the contents of an existing file using a series of read()
    operations.
    """

    def __init__(self,fileobj,cipher,mode=None):
        """EncryptFile Constructor.
        <fileobj> is the file object with decrypted contents, and <cipher>
        is the cipher object to be used.  <mode> must be one of "r" or "w"
        to specify whether reading or writing is desired.  If omitted, the
        mode of <fileobj> is used if possible.  Otherwise, "r" is assumed.
        """
        self.__cipher = cipher
        myFileObj = TransFile(fileobj,self.__crypt,mode)
        self.mode = myFileObj.mode
        myFileObj = FixedBlockSizeFile(myFileObj,cipher.block_size)
        FileWrapper.__init__(self,myFileObj)
    
    def __crypt(self,data):
        """Encrypt/decrypt the given data depending on file mode.
        If mode is "r" then the data is encrypted.  Otherwise, it is
        decrypted.
        """
        if self.mode == "r":
            # if len(data) is not a multiple of the blocksize, it must
            # be the last data before EOF.  Pad it as appropriate
            if len(data) % self.__cipher.block_size != 0:
                data = self._fileobj._pad_to_size(data)
            return self.__cipher.encrypt(data)
        return self.__cipher.decrypt(data)


class Test_CryptFiles(unittest.TestCase):
    """Testcases for the (En/De)CryptFile classes."""
    
    def setUp(self):
        import StringIO
        from Crypto.Cipher import DES
        # Example inspired by the PyCrypto manual
        self.cipher = DES.new('abcdefgh',DES.MODE_ECB)
        self.plaintextin = "Guido van Rossum is a space alien."
        self.plaintextout = "Guido van Rossum is a space alien." + "\0"*6
        self.ciphertext = "\x11,\xe3Nq\x8cDY\xdfT\xe2pA\xfa\xad\xc9s\x88\xf3,\xc0j\xd8\xa8\xca\xe7\xe2I\xd15w\x1d\xfe\x92\xd7\xca\xc9\xb5r\xec"
        self.plainfile = StringIO.StringIO(self.plaintextin)
        self.cryptfile = StringIO.StringIO(self.ciphertext)
        self.outfile = StringIO.StringIO()

    def tearDown(self):
        pass

    def test_ReadDecrypt(self):
        """Test reading from an encrypted file."""
        df = DecryptFile(self.cryptfile,self.cipher,"r")
        self.assert_(df.read() == self.plaintextout)

    def test_ReadEncrypt(self):
        """Test reading from a decrypted file."""
        ef = EncryptFile(self.plainfile,self.cipher,"r")
        self.assert_(ef.read() == self.ciphertext)
    
    def test_WriteDecrypt(self):
        """Test writing to an encrypted file."""
        df = DecryptFile(self.outfile,self.cipher,"w")
        df.write(self.plaintextin)
        df.flush()
        self.assert_(self.outfile.getvalue() == self.ciphertext)
        
    def test_WriteEncrypt(self):
        """Test writing to a decrypted file."""
        ef = EncryptFile(self.outfile,self.cipher,"w")
        ef.write(self.ciphertext)
        self.assert_(self.outfile.getvalue() == self.plaintextout)
    

def testsuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_TransFile))
    suite.addTest(unittest.makeSuite(Test_FixedBlockSizeFile))
    suite.addTest(unittest.makeSuite(Test_CryptFiles))
    return suite


# Run regression tests when called from comand-line
if __name__ == "__main__":
    UnitTest.TextTestRunner().run(testsuite())