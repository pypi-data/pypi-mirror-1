# $Id$
# requestbuffer.py - help for dealing with various character encodings
#
# Copyright (C) 2006 Geoffrey T. Dairiki <dairiki@dairiki.org>
#                and Michael Bayer <mike_mp@zzzcomputing.com>
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
import codecs, sys, StringIO
        
class _Link(object):
    def __init__(self, parent):
        self.parent = parent
    
    def write(self, text):
        """Write text to the buffer chain.

        See also `RequestBuffer.write()`_.
        """
        raise NotImplementedError, "(pure virtual)"
    
    def flush(self):
        pass

    def clear(self):
        pass

    def __repr__(self):
        return "<%s: Parent:\n %s>" % (
            object.__repr__(self)[1:-1], repr(self.parent))

class _Buffer(_Link):
    def __init__(self, parent, buffer=None):
        _Link.__init__(self, parent)
        if buffer is None:
            buffer = StringIO.StringIO()
        self.buffer = buffer
        self.write = self.buffer.write

    def write(self, text):
        # XXX: Note that this method never really gets called.
        #      (See __init__.)
        self.buffer.write(text)
        
    def flush(self):
        self.buffer.seek(0)
        self.parent.write(self.buffer.read())
        self.clear()
        
    def clear(self):
        self.buffer.truncate(0)
        # work around for bug in python2.3's cStringIO:
        try: self.buffer.seek(0)
        except: pass

class _TransparentBuffer(_Buffer):
    """A buffer which defers all recoding.
    """
    def __init__(self, parent):
        _Link.__init__(self, parent)
        self._buf = []

    def write(self, text):
        self._buf.append(text)

    def flush(self):
        self.parent.write(''.join(self._buf))
        self.clear()

    def clear(self):
        self._buf = []

class _CaptureBuffer(_Buffer):
    """A buffer used to capture output.
    """
    pass
    
class _EncodedBuffer(_Buffer):
    """This is a buffer which expects encoded strings.
    """
    def __init__(self, parent, buffer,
                 encoding=sys.getdefaultencoding(), errors='strict'):
        _Buffer.__init__(self, parent, buffer)
        self._writer = None
        self.set_encoding(encoding, errors)
        
    def set_encoding(self, encoding, errors):
        if self._writer:
            self._writer.reset()
        stream_writer = codecs.lookup(encoding)[3]
        self._writer = stream_writer(self.buffer, errors)
        self.write = self._writer.write
        self.__encoding = (encoding, errors)

    def write(self, text):
        self._writer.write(text)
        
    def flush(self):
        self._writer.reset()
        _Buffer.flush(self)
        
    def clear(self):
        self._writer.reset()
        _Buffer.clear(self)

    def get_encoding(self):
        return self.__encoding[0]
    encoding = property(get_encoding,
                        doc="Encoding of the output stream.")
    
    def get_errors(self):
        return self.__encoding[1]
    errors = property(get_errors,
                      doc="Encoding error handling strategy of the output stream.")
    
class _StrBuffer(_Buffer):
    """This is a buffer which strs.
    """
    def __init__(self, parent, buffer):
        _Buffer.__init__(self, parent, buffer)

    def get_encoding(self):
        return None
    encoding = property(get_encoding,
                        doc="Encoding of the output stream.")
    
    def get_errors(self):
        return None
    errors = property(get_errors,
                      doc="Encoding error handling strategy of the output stream.")

class _Filter(_Link):
    def __init__(self, parent, filter):
        _Link.__init__(self, parent)
        self.filter = filter

class _UnicodeFilter(_Filter):
    def write(self, text):
        self.parent.write(unicode(self.filter(text)))

class _StrFilter(_Filter):
    def write(self, text):
        self.parent.write(str(self.filter(text)))

################################################################

class MismatchedPop(Exception):
    pass


class _RequestBuffer(object):
    def __init__(self, top):
        self._top = self.__root = top

    def push_buffer(self):
        '''Push a component output buffer.

        These buffers are used to buffer component output temporarily.
        When the buffer is flushed, it passes it contents on to the next
        buffer in the stack.  Normally the buffers are flushed when
        they are popped off the stack.
        '''
        self.__push(_TransparentBuffer)

    def pop_buffer(self, discard=False):
        """Pop a component output buffer

        The argument ``discard``, if set,
        specifies that the contents of the buffer are to be discarded,
        rather than passed on to the next buffer in the stack.
        """
        buf = self.__pop(_TransparentBuffer)
        if not discard:
            buf.flush()

    def push_filter(self, filter):
        """Push a filter.

        The filter function gets passed either a ``unicode`` or
        a system default encoded ``str``.

        If the ``disable_unicode`` config parameter is set, the filter
        always gets a ``str``.

        The filter can return any type acceptable to the `write`_ method.
        """
        self.__push(self._FilterType, filter=filter)

    def pop_filter(self):
        """Pop a filter.

        Returns the filter function.
        """
        return self.__pop(self._FilterType).filter
    
    def push_capture_buffer(self, buffer=None):
        """Push a capture buffer.

        This is a buffer used to capture component output.
        It does not propagate its contents down the buffer chain
        when it is popped.

        The ``buffer`` should be a file-like object supporting
        at least the ``write()`` method.  The strings passed to
        ``buffer.write()`` will be ``unicode``s or system default
        (usually ASCII) encoded ``str``s.
        """
        self.__push(_CaptureBuffer, buffer=buffer)

    def pop_capture_buffer(self):
        """Pop a capture buffer of the stack.

        Returns the underlying buffer.
        """
        return self.__pop(_CaptureBuffer).buffer

    def __push(self, link_class, **kw):
        self._top = link_class(self._top, **kw)
        return self._top
    
    def __pop(self, *expected_link_classes):
        link = self._top
        if not isinstance(link, expected_link_classes):
            raise MismatchedPop, \
                  "RequestBuffer.pop* expected %s, got %s" \
                  % ( repr(map(lambda x: x.__name__, expected_link_classes)),
                      link.__class__.__name__ )
        self._top = link.parent
        return link

    def get_state(self):
        """Get the current state of the buffer stack.

        Returns an opaque value, which can be pssed to `pop_to_state`_
        to restore the buffer to it's current state.
        """
        return (self._top,)

    def pop_to_state(self, state, discard=False):
        """Pop buffers, and restore saved state.

        Buffers are popped from the stack back to the position
        of the saved state.   (The buffers are flushed as they are
        popped, unless ``discard`` parameter is set.)
        After the stack is unwound, the ``errors``
        attribute is restored to what it was at the time the
        state was saved.

        If a ``UnicodeError`` is thrown while flushing buffers,
        no further buffers are flushed.  However the stack is still
        unwound and the buffer state restored before the exception
        is re-raised.
        """
        top, = state
        if not isinstance(top, _Link):
            raise ValueError, "invalid state"
        
        bufs_to_flush = []

        for b in self.__bufs(end=None):
            if b is top:
                break
            elif not isinstance(b, _CaptureBuffer):
                bufs_to_flush.append(b)
        else:
            # states top is not in our stack
            raise ValueError, "invalid state"

        try:
            if not discard:
                for buf in bufs_to_flush:
                    buf.flush()
        finally:
            self._top = top

    def __bufs(self, begin=None, end="root"):
        if begin is None:
            begin = self._top
        if end == "root":
            end = self.__root
        b = begin
        while b is not end:
            yield b
            b = b.parent
            

    def write(self, text):
        """Write text to the buffer.
        """
        raise NotImplementedError, "pure virtual"

    def flush(self):
        """Flush output.

        Output is flushed up the first capture buffer in the stack.  If
        there is no capture buffer, then output is flushed all the way
        to the final output buffer.
        """
        for buf in self.__bufs():
            if isinstance(buf, _CaptureBuffer):
                break
            buf.flush()

    def clear(self):
        """Clears all buffers in the stack.
        """
        for buf in self.__bufs():
            buf.clear()

    encoding = property(
        lambda self: self.__root.encoding,
        doc="""The current output encoding of the buffer.

        Output written to the underlying output buffer (e.g.
        the Apache request object) are encoded using this encoding.
        """)

    errors = property(
        lambda self: self.__root.errors,
        doc="""The current encoding error handling strategy.

        This is the error handling strategy of the underlying output
        buffer.
        """)

    def set_encoding(self, encoding, errors='strict'):
        """Set encoding of output to the final buffer.
        """
        self.__root.set_encoding(encoding, errors)
        
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, repr(self._top))

class UnicodeRequestBuffer(_RequestBuffer):

    _FilterType = _UnicodeFilter
    
    def __init__(self, output_buffer, output_encoding, errors='strict'):
        """Constructor.

        The ``output_buffer`` is assumed to be a buffer like stdout
        or an apache request object, so we will not do anything
        but ``.write()`` to it.
        """
        top = _EncodedBuffer(None, output_buffer, output_encoding, errors)
        _RequestBuffer.__init__(self, top)

    def write(self, text):
        """Write text to the buffer.

        .. _`RequestBuffer.write()`:
        
        If ``text`` is a plain ``str``, it is interpreted according
        to the value of the system default encoding
        (obtainable from ``sys.getdefaultencoding()``.)

        Otherwise, if ``text`` is a ``unicode`` object or has a
        ``__unicode__`` method, it is treated as unicode.

        Finally, if ``text`` is neither a ``str`` nor convertable to
        a ``unicode``, it is coerced to a ``str`` and interpreted
        according to the system default encoding.
        """
        if text is None:
            return
        self._top.write(unicode(text))

class StrRequestBuffer(_RequestBuffer):

    _FilterType = _StrFilter
    
    def __init__(self, output_buffer):
        """Constructor.

        The ``output_buffer`` is assumed to be a buffer like stdout
        or an apache request object, so we will not do anything
        but ``.write()`` to it.
        """
        _RequestBuffer.__init__(self, _StrBuffer(None, output_buffer))

    def write(self, text):
        """Write text to the buffer.
        """
        if text is None:
            return
        self._top.write(str(text))

