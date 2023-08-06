# Copyright (c) 2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.


"""
General utility functions used within pesto.

These functions are reserved for internal usage and it is not recommended that
users of the API call these functions directly
"""
from collections import deque
from cStringIO import StringIO, OutputType as cStringIO_OutputType
from itertools import chain, repeat
from shutil import copyfileobj
from tempfile import TemporaryFile

class MultiDict(dict):
    """
    Like a dictionary, but supports multiple values per key.

    Synopsis::

        >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        >>> d['a']
        1
        >>> d['b']
        3
        >>> d.getlist('a')
        [1, 2]
        >>> d.getlist('b')
        [3]

    """

    def __init__(self, posarg=None, **kwargs):
        """
        MultiDicts can be constructed in the following ways:

            1. From a sequence of ``(key, value)`` pairs::

                >>> MultiDict([('a', 1), ('a', 2)])
                MultiDict([('a', 1), ('a', 2)])

            2. Initialized from another MultiDict::

                >>> d = MultiDict([('a', 1), ('a', 2)])
                >>> MultiDict(d)
                MultiDict([('a', 1), ('a', 2)])

            3. Initialized from a regular dict::

                >>> MultiDict({'a': 1})
                MultiDict([('a', 1)])

            4. From keyword arguments::

                >>> MultiDict(a=1)
                MultiDict([('a', 1)])

        """
        dict.__init__(self)

        if posarg is None:
            posarg = []

        if isinstance(posarg, self.__class__):
            posarg = posarg.iterallitems()

        if isinstance(posarg, dict):
            posarg = posarg.items()

        for key, value in chain(posarg, kwargs.items()):
            dict.setdefault(self, key, []).append(value)

    def __getitem__(self, key):
        """
        Return the first item associated with ``key``::

            >>> d = MultiDict([('a', 1), ('a', 2)])
            >>> d['a']
            1
        """
        try:
            return dict.__getitem__(self, key)[0]
        except IndexError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Set the items associated to a list of one item, ``value``.

            >>> d = MultiDict()
            >>> d['b'] = 3
            >>> d
            MultiDict([('b', 3)])
        """
        return dict.__setitem__(self, key, [value])

    def get(self, key, default=None):
        """
        Return the first available value for key ``key``, or ``default`` if no
        value exists.
        """
        try:
            return dict.get(self, key, [])[0]
        except IndexError:
            return default

    def getlist(self, key):
        """
        Return a list of all values for key ``key``.
        """
        return dict.get(self, key, [])

    def copy(self):
        """
        Return a shallow copy of the dictionary::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> copy = d.copy()
            >>> copy
            MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> copy is d
            False
        """
        return MultiDict(self)


    def fromkeys(cls, seq, value=None):
        """
        Create a new MultiDict with keys from seq and values set to value.

        Example::

            >>> MultiDict.fromkeys(['a', 'b'])
            MultiDict([('a', None), ('b', None)])

        Keys can be repeated::

            >>> d = MultiDict.fromkeys(['a', 'b', 'a'])
            >>> d.getlist('a')
            [None, None]
            >>> d.getlist('b')
            [None]

        """
        return cls(zip(seq, repeat(value)))
    fromkeys = classmethod(fromkeys)

    def items(self):
        """
        Return a list of ``(key, value)`` tuples. Only the first ``(key,
        value)`` is returned where keys have multiple values::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.items())
            [('a', 1), ('b', 3)]
        """
        return list(self.iteritems())

    def iteritems(self):
        """
        Like ``items``, but return an iterator rather than a list.
        """
        for key in self.iterkeys():
            yield key, self[key]

    def listitems(self):
        """
        Like ``items``, but returns lists of values::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.listitems())
            [('a', [1, 2]), ('b', [3])]
        """
        return dict.items(self)

    def iterlistitems(self):
        """
        Like ``listitems``, but return an iterator rather than a list.
        """
        return dict.iteritems(self)

    def allitems(self):
        """
        Return a list of ``(key, value)`` pairs for each item in the MultiDict.
        Items with multiple keys will have multiple key-value pairs returned::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.allitems())
            [('a', 1), ('a', 2), ('b', 3)]
        """
        return list(self.iterallitems())

    def iterallitems(self):
        """
        Like ``allitems``, but return an iterator rather than a list.
        """
        for key, values in dict.iteritems(self):
            for value in values:
                yield key, value

    def values(self):
        """
        Return values from the dictionary. Where keys have multiple values,
        only the first is returned::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.values())
            [1, 3]
        """
        return list(self.itervalues())

    def itervalues(self):
        """
        Like ``values``, but return an iterator rather than a list.
        """
        for key in self.iterkeys():
            yield self[key]

    def listvalues(self):
        """
        Return a list of values. Each item returned is a the list of values associated with a single key.

        Example usage::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.listvalues())
            [[1, 2], [3]]
        """
        return list(self.iterlistvalues())

    def iterlistvalues(self):
        """
        Like ``listvalues``, but returns an iterator over the results instead of a list.
        """
        return dict.itervalues(self)

    def pop(self, key, default=None):
        """
        Dictionary ``pop`` method. Return and remove the value associated with
        ``key``. If more than one value is associated with ``key``, only the
        first is returned.
        """
        try:
            return dict.pop(self, key, default)[0]
        except IndexError:
            raise KeyError(key)

    def popitem(self):
        """
        Dictionary ``popitem`` method.
        """
        try:
            return dict.pop(self)[0]
        except IndexError:
            raise KeyError()

    def setdefault(self, key, default=None):
        """
        Dictionary ``setdefault`` method.
        """
        return dict.setdefault(self, key, [default])[0]

    def update(self, other=None, **kwargs):
        """
        Update the MultiDict from another MultiDict::

                >>> d = MultiDict()
                >>> d.update(MultiDict([('a', 1), ('a', 2)]))
                >>> d
                MultiDict([('a', 1), ('a', 2)])

        dictionary::

                >>> d = MultiDict()
                >>> d.update({'a': 1, 'b': 2})
                >>> d
                MultiDict([('a', 1), ('b', 2)])

        iterable of key, value pairs::

                >>> d = MultiDict()
                >>> d.update([('a', 1), ('b', 2)])
                >>> d
                MultiDict([('a', 1), ('b', 2)])

        Note that in this case, repeated keys in the iterable are ignored. The
        effect is the same as calling ``update`` once for each repeated key::

                >>> d = MultiDict()
                >>> d.update([('a', 1), ('a', 2)])
                >>> d
                MultiDict([('a', 2)])
             
        or keyword arguments::

                >>> d = MultiDict()
                >>> d.update(a=1, b=2)
                >>> d
                MultiDict([('a', 1), ('b', 2)])

        """
        if other is None:
            items = []
        elif isinstance(other, self.__class__):
            items = other.iterlistitems()
        elif isinstance(other, dict):
            items = [(key, [item]) for key, item in other.iteritems()]
        else:
            items = [(key, [item]) for key, item in iter(other)]

        items = chain(items, [(key, [item]) for key, item in kwargs.iteritems()])

        for key, values in items:
            dict.__setitem__(self, key, values)

    def __repr__(self):
        """
        ``__repr__`` representation of object
        """
        return '%s(%r)' % (self.__class__.__name__, self.allitems())

    def __str__(self):
        """
        ``__str__`` representation of object
        """
        return repr(self)


class ReadlinesMixin(object):
    """
    Mixin that defines readlines and the iterator interface in terms of
    underlying readline method.
    """

    def readlines(self, sizehint=0):
        size = 0
        lines = []
        for line in iter(self.readline, ''):
            lines.append(line)
            size += len(line)
            if 0 < sizehint <= size:
                break
        return lines

    def __iter__(self):
        return self

    def next(self):
        return self.readline()


class PutbackInput(ReadlinesMixin):
    r"""
    Wrap a file-like object to allow data read to be returned to the buffer.

    Only supports serial read-access, ie no seek or write methods.

    Example::

        >>> from StringIO import StringIO
        >>> s = StringIO("the rain in spain\nfalls mainly\non the plain\n")
        >>> p = PutbackInput(s)
        >>> line = p.readline()
        >>> line
        'the rain in spain\n'
        >>> p.putback(line)
        >>> p.readline()
        'the rain in spain\n'
    """

    def __init__(self, io):
        """
        Initialize a ``PutbackInput`` object from input stream ``io``.
        """
        self._io = io
        self._putback = deque()

    def read(self, size=-1):
        """
        Return up to ``size`` bytes from the input stream.
        """

        if size < 0:
            result = ''.join(self._putback) + self._io.read()
            self._putback.clear()
            return result

        buf = []
        remaining = size
        while remaining > 0 and self._putback:
            chunk = self._putback.popleft()
            excess = len(chunk) - remaining
            if excess > 0:
                chunk, p = chunk[:-excess], chunk[-excess:]
                self.putback(p)

            buf.append(chunk)
            remaining -= len(chunk)

        if remaining > 0:
            buf.append(self._io.read(remaining))

        return ''.join(buf)

    def readline(self, size=-1):
        """
        Read a single line of up to ``size`` bytes from the input stream.
        """

        remaining = size
        buf = []
        while self._putback and (size < 0 or remaining > 0):
            chunk = self._putback.popleft()

            if size > 0:
                excess = len(chunk) - remaining
                if excess > 0:
                    chunk, p = chunk[:-excess], chunk[-excess:]
                    self.putback(p)

            pos = chunk.find('\n')
            if pos >= 0:
                chunk, p = chunk[:(pos+1)], chunk[(pos+1):]
                self.putback(p)
                buf.append(chunk)
                return ''.join(buf)

            buf.append(chunk)
            remaining -= len(chunk)

        if size > 0:
            buf.append(self._io.readline(remaining))
        else:
            buf.append(self._io.readline())

        return ''.join(buf)

    def putback(self, data):
        """
        Put ``data`` back into the stream
        """
        self._putback.appendleft(data)

    def peek(self, size):
        """
        Peek ahead ``size`` bytes from the stream without consuming any data
        """
        peeked = self.read(size)
        self.putback(peeked)
        return peeked

class SizeLimitedInput(ReadlinesMixin):
    r"""
    Wrap an IO object to prevent reading beyond ``length`` bytes.

    Example::

        >>> from StringIO import StringIO
        >>> s = StringIO("the rain in spain\nfalls mainly\non the plain\n")
        >>> s = SizeLimitedInput(s, 24)
        >>> len(s.read())
        24
        >>> s.seek(0)
        >>> s.read()
        'the rain in spain\nfalls '
        >>> s.seek(0)
        >>> s.readline()
        'the rain in spain\n'
        >>> s.readline()
        'falls '
    """

    def __init__(self, io, length):
        self._io = io
        self.length = length
        self.pos = 0

    def check_available(self, requested):
        """
        Return the minimum of ``requested`` and the number of bytes available
        in the stream. If ``requested`` is negative, return the number of bytes
        available in the stream.
        """
        if requested < 0:
            return self.length - self.pos
        else:
            return min(self.length - self.pos, requested)

    def tell(self):
        """
        Return the position of the file pointer in the stream.
        """
        return self.pos

    def seek(self, pos, whence=0):
        """
        Seek to position ``pos``. This is a wrapper for the underlying IO's
        ``seek`` method.
        """
        self._io.seek(pos, whence)
        self.pos = self._io.tell()

    def read(self, size=-1):
        """
        Return up to ``size`` bytes from the input stream.
        """
        size = self.check_available(size)
        result = self._io.read(size)
        self.pos += len(result)
        return result

    def readline(self, size=-1):
        """
        Read a single line of up to ``size`` bytes from the input stream.
        """
        size = self.check_available(size)
        result = self._io.readline(self.check_available(size))
        self.pos += len(result)
        return result


class DelimitedInput(ReadlinesMixin):

    r"""
    Wrap a PutbackInput to read as far as a delimiter (after which subsequent
    reads will return empty strings, as if EOF was reached)

    Examples::

        >>> from StringIO import StringIO
        >>> s = StringIO('one--two--three')
        >>> s.seek(0)
        >>> p = PutbackInput(s)
        >>> DelimitedInput(p, '--').read()
        'one'
        >>> DelimitedInput(p, '--').read()
        'two'
        >>> DelimitedInput(p, '--').read()
        'three'
        >>> DelimitedInput(p, '--').read()
        ''

    """

    def __init__(self, io, delimiter, consume_delimiter=True):
        """
        Initialize an instance of ``DelimitedInput``.
        """

        if not getattr(io, 'putback', None):
            raise TypeError("Need an instance of PutbackInput")

        self._io = io
        self.delimiter = delimiter
        self.consume_delimiter = consume_delimiter
        self.delimiter_found = False

    def read(self, size=-1):
        """
        Return up to ``size`` bytes of data from the stream until EOF or
        ``delimiter`` is reached.
        """
        if self.delimiter_found:
            return ''
        MAX_BLOCK_SIZE = 8 * 1024
        if size == -1:
            return ''.join(iter(lambda: self.read(MAX_BLOCK_SIZE), ''))

        data = self._io.read(size + len(self.delimiter))
        pos = data.find(self.delimiter)
        if pos >= 0:
            putback = data[pos+len(self.delimiter):] if self.consume_delimiter else data[pos:]
            self.delimiter_found = True
            self._io.putback(putback)
            return data[:pos]

        elif len(data) == size + len(self.delimiter):
            self._io.putback(data[-len(self.delimiter):])
            return data[:-len(self.delimiter)]

        else:
            return data

    def readline(self, size=-1):
        """
        Read a single line of up to ``size`` bytes from the input stream, or up
        to ``delimiter`` if this is encountered before a complete line is read.
        """

        if self.delimiter_found:
            return ''
        line = self._io.readline(size)
        extra = self._io.read(len(self.delimiter))
        if self.delimiter not in line+extra:
            self._io.putback(extra)
            return line

        data = line + extra
        pos = data.find(self.delimiter)
        if pos >= 0:
            putback = data[pos+len(self.delimiter):] if self.consume_delimiter else data[pos:]
            self.delimiter_found = True
            self._io.putback(putback)
            return data[:pos]
        elif len(data) == size + len(self.delimiter):
            self._io.putback(data[-len(self.delimiter):])
            return data[:-len(self.delimiter)]
        else:
            return data


class ExpandableOutput(object):
    """
    Write-only output object.

    Will store data in a StringIO, until more than ``bufsize`` bytes are
    written, at which point it will switch to storing data in a real file
    object.
    """

    def __init__(self, bufsize=16384):
        """
        Initialize an ``ExpandableOutput`` instance.
        """
        self._io = StringIO()
        self.bufsize = bufsize
        self.write = self.write_stringio
        self.exceeded_bufsize = False

    def write_stringio(self, data):
        """
        ``write``, optimized for the StringIO backend.
        """
        if isinstance(self._io, cStringIO_OutputType) and self.tell() + len(data) > self.bufsize:
            self.switch_to_file_storage()
            return self.write_file(data)
        return self._io.write(data)

    def write_file(self, data):
        """
        ``write``, optimized for the TemporaryFile backend
        """
        return self._io.write(data)

    def switch_to_file_storage(self):
        """
        Switch the storage backend to an instance of ``TemporaryFile``.
        """
        self.exceeded_bufsize = True
        oldio = self._io
        try:
            self._io.seek(0)
            self._io = TemporaryFile()
            copyfileobj(oldio, self._io)
        finally:
            oldio.close()
        self.write = self.write_file

    def __getattr__(self, attr):
        """
        Delegate to ``self._io``.
        """
        return getattr(self._io, attr)

    def __enter__(self):
        """
        Support for context manager ``__enter__``/``__exit__`` blocks
        """
        return self

    def __exit__(self, type, value, traceback):
        """
        Support for context manager ``__enter__``/``__exit__`` blocks
        """
        self._io.close()
        # propagate exceptions
        return False

