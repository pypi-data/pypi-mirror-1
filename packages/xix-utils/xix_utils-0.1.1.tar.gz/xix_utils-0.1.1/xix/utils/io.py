#!/usr/bin/env python
"""IO batteries

$Id: io.py 159 2005-12-02 20:35:19Z drew $
"""

from cStringIO import StringIO
import fileinput

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright 2005, Drew Smathers'
__revision__ = '$Revision: 159 $'


class AggregateFileInput:
    """Similar to AggregateFile except much faster and only iteration is
    supported
    """

    def __init__(self, files):
        self.files = files

    def __iterfiles(self):
        last = ''
        for line in fileinput.input(self.files):
            if line[-1] != '\n':
                last = line
            else:
                yield last + line
                last = ''
        if last:
            yield last # TODO unit test this

    def __iter__(self):
        return self.__iterfiles()

    def readlines(self):
        # alias
        return self.__iterfiles()

class AggregateFile:
    """A file-like object that aggregates multiple files into one
    virtual file handle.  Current supported operations are read-only
    and consist of read, readline, seek, and tell.

    TODO: optimizations
    """

    def __init__(self, files):
        self.files = files
        self.fds = []
        self.focus_idx = 0
        self.seek_amounts = []

    def open(self):
        """Open the file descriptors for files mananged by this instance.
        """
        aggrlen = 0
        for fname in self.files:
            fd = open(fname)
            self.fds.append(fd)
            # Calculate the len of this file
            fd.seek(0, 2)
            aggrlen += fd.tell()
            self.seek_amounts.append(aggrlen)
            fd.seek(0)
        return self

    def seek(self, offset, whence=0):
        if whence == 0:
            self.__seek_from_start(offset)
        elif whence == 1:
            self.__seek_from_curr(offset)
        elif whence == 2:
            self.__seek_from_eof(offset)
        else:
            raise IOError, '[Error 22] Invalid argument'

    def __seek_from_start(self, offset):
        fds = self.fds
        self.focus_idx = 0
        vpos = 0
        amts = self.seek_amounts
        voff = offset
        fd = fds[self.focus_idx]
        fd.seek(0)
        fd.seek(voff)
        while offset > amts[self.focus_idx] \
                and self.focus_idx < len(fds) - 1:
            voff -= amts[self.focus_idx]
            self.focus_idx += 1
            fd = fds[self.focus_idx]
            fd.seek(0)
            fd.seek(voff)
        
    def __seek_from_curr(self, offset):
        fds = self.fds
        currpos = fds[self.focus_idx].tell()
        vpos = 0
        voff = offset
        if offset < 0:
            voff *= -1 # make positive
            while voff > currpos and self.focus_idx > 0:
                voff -= currpos
                self.focus_idx -= 1
                fds[self.focus_idx].seek(0, 2)
                currpos = fds[self.focus_idx].tell()
            fds[self.focus_idx].seek(-voff, 1)
        else:
            voff = offset
            amts = self.seek_amounts
            while self.tell() + offset > amts[self.focus_idx] \
                    and self.focus_idx < len(fds) - 1:
                voff -= (amts[self.focus_idx] - self.tell())
                self.focus_idx += 1
                fds[self.focus_idx].seek(0)
            fds[self.focus_idx].seek(voff, 1)

    
    def __seek_from_eof(self, offset):
        fd = self.fds[len(self.fds) - 1]
        fd.seek(0,2)
        self.focus_idx = len(self.fds) - 1
        self.__seek_from_curr(offset)

    def tell(self):
        amt = self.fds[self.focus_idx].tell()
        if self.focus_idx > 0:
            amt += self.seek_amounts[self.focus_idx - 1]
        return amt


    def read(self, count=-1):
        fds = self.fds
        buffer = StringIO()
        if count < 0:
            buffer.write(fds[self.focus_idx].read())
            self.focus_idx += 1
            while self.focus_idx < len(fds):
                fds[self.focus_idx].seek(0)
                buffer.write(fds[self.focus_idx].read())
                self.focus_idx += 1
            self.focus_idx = len(self.fds) - 1
        else:
            amts = self.seek_amounts
            currpos = self.tell()
            ct = count
            bytes = fds[self.focus_idx].read(ct)
            buffer.write(bytes)
            while ct + currpos > amts[self.focus_idx] \
                    and self.focus_idx < len(fds) - 1:
                self.focus_idx += 1
                ct -= len(bytes)
                bytes = fds[self.focus_idx].read(ct)
                fds[self.focus_idx].seek(0)
                buffer.write(fds[self.focus_idx].read(ct))
                currpos = self.tell()
        return buffer.getvalue()
            
    def __iter__(self):
        return self.readlines()

    def readline(self):
        """Lines which span one file to the next are returned
        in whole by calls to readline.
        """
        buffer = StringIO()
        byte = self.read(1)
        buffer.write(byte)
        while byte and byte != '\n':
            byte = self.read(1)
            buffer.write(byte)
        return buffer.getvalue()

    def readlines(self):
        """Generate lines in this aggregate file.
        """
        line = self.readline()
        while line:
            yield line
            line = self.readline()
        
