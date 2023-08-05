# $Id: buffer.py 2133 2006-09-06 18:52:56Z dairiki $
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
import string

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
