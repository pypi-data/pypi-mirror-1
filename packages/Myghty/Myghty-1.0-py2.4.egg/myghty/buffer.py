# $Id: buffer.py 2013 2005-12-31 03:19:39Z zzzeek $
# buffer.py - string buffering functions for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

"""Buffer is an output handling object which corresponds to the Python file object
interface."""

from myghty.util import *
import StringIO
import sys, string

class BufferDecorator(object):
    """allows flexible combinations of buffers.  """
    
    def __init__(self, buffer):
        self.buffer = buffer
        
    def __getattr__(self, name):
        return getattr(self.buffer, name)
        
    def __repr__(self):
        return "BufferDecorator, enclosing %s." % repr(self.buffer)

class FunctionBuffer(BufferDecorator):
    def __init__(self, func):
        self.func = func
    def write(self, s):
        self.func(s)

class LinePrinter(BufferDecorator):
    def write(self, s):
        self.buffer.write(s + "\n")
    def writelines(self, list):
        self.buffer.writelines([s + "\n" for s in list])

class HierarchicalBuffer(BufferDecorator):
    """a buffer that can create child buffers or itself be attached to a parent
    buffer"""
    def __init__(self, buffer = None, parent = None, ignore_flush = False, ignore_clear = False, filter = None):
        self.parent = parent
        if buffer is None and parent is not None:
            BufferDecorator.__init__(self, parent.buffer)
        else:
            BufferDecorator.__init__(self, buffer)
            
        self.ignore_flush = ignore_flush
        self.ignore_clear = ignore_clear
        self.filter = filter

    def add_child(self, buffer):
        return HierarchicalBuffer(buffer,  parent = self)

    def truncate(self, size=None):
        if not self.ignore_clear:
            return self.buffer.truncate(size)

    def write(self, s):
        if self.filter:
            self.buffer.write(self.filter(s))
        else:
            self.buffer.write(s)

    def writelines(self, list):
        if self.filter:
            self.buffer.write(map(self.filter, list))
        else:
            self.buffer.write(list)

    def flush(self):
        if not self.ignore_flush:
            if self.parent:
                self.buffer.seek(0)
                self.parent.write(self.buffer.read())
                self.buffer.truncate(0)
            else:
                self.buffer.flush()

    def __repr__(self):
        return "Hierarchical Buffer, enclosing %s.  Parent:\n %s" % (repr(self.buffer), repr(self.parent))



class LogFormatter(BufferDecorator):
    def __init__(self, buffer, identifier, id_threads = False, autoflush = True):
        BufferDecorator.__init__(self, buffer)
        self.identifier = identifier
        self.id_threads = id_threads
        self.autoflush = autoflush
        
    def _formatline(self, s):
        if self.id_threads:
            return "[%s] [pid:%d tid:%d] %s" % (self.identifier, pid(), thread_id(), string.rstrip(s))
        else:
            return "[%s] %s" % (self.identifier, string.rstrip(s))
        
    def write(self, s):
        self.buffer.write(self._formatline(s))
        if self.autoflush:
            self.flush()
        
    def writelines(self, lines):
        for line in lines:
            self.buffer.write(self._formatline(line))
