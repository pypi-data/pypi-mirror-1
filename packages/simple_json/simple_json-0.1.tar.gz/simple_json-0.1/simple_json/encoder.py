#!/usr/bin/env python
import re

ESCAPE = re.compile(r'[\x00-\x19\\"\b\f\n\r\t]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
for i in range(20):
    ESCAPE_DCT[chr(i)] = '\\u%04x' % (i,)

SINGLETONS = {
    None: 'null',
    True: 'true',
    False: 'false',
}

def encode_basestring(s):
    """
    Return a JSON representation of a Python string
    """
    def replace(match):
        return ESCAPE_DCT[match.group(0)]
    return '"' + ESCAPE.sub(replace, s) + '"'

class JSONEncoder(object):
    """
    Extensible JSON <http://json.org> encoder for Python data structures.

    Supports the following objects and types by default:
    
    - None (null)
    - True, False (bool)
    - float, int, long (number)
    - str, unicode (string)
    - dict (object)
    - list, tuple (array)

    To extend this to recognize other objects, subclass and replace the
    default method with another method that returns one of the above
    serializable objects.
    """
    def __init__(self, skipkeys=False):
        """
        If skipkeys is False (the default), then it is a TypeError to attempt
        encoding of keys that are not strings or numbers.
        
        If skipkeys is True, such items are simply skipped.
        """
        
        self.skipkeys = skipkeys

    def iterencode_list(self, lst):
        if not lst:
            yield '[]'
            return
        yield '['
        first = True
        for value in lst:
            if first:
                first = False
            else:
                yield ', '
            for chunk in self.iterencode(value):
                yield chunk
        yield ']'

    def iterencode_dict(self, dct):
        if not dct:
            yield '{}'
            return
        yield '{'
        first = True
        for key, value in dct.iteritems():
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            if isinstance(key, (int, long, float)):
                key = str(key)
            if not isinstance(key, basestring):
                if self.skipkeys:
                    continue
                else:
                    raise TypeError("key %r is not a string" % (key,))
            if first:
                first = False
            else:
                yield ', '
            yield encode_basestring(key)
            yield ':'
            for chunk in self.iterencode(value):
                yield chunk
        yield '}'

    def iterencode(self, o):
        """
        Encode the given object and yield each string
        representation as available.  For example::
            
            for chunk in encoder.iterencode(bigobject):
                mysocket.write(chunk)
        """
        if isinstance(o, basestring):
            yield encode_basestring(o)
            return
        if isinstance(o, (int, long, float)) and not isinstance(o, bool):
            yield str(o)
            return
        if isinstance(o, (list, tuple)):
            for chunk in self.iterencode_list(o):
                yield chunk
            return
        if isinstance(o, dict):
            for chunk in self.iterencode_dict(o):
                yield chunk
            return
        try:
            yield SINGLETONS[o]
            return
        except (TypeError, KeyError):
            pass
        for chunk in self.iterencode_default(o):
            yield chunk

    def iterencode_default(self, o):
        newobj = self.default(o)
        return self.iterencode(newobj)

    def default(self, o):
        """
        When subclassing JSONEncoder, replace this with a method
        that returns an encodable object instead of o.  For example,
        to support arbitrary iterators, you might implement default
        like this::
            
            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)
        """
        raise TypeError("%r is not JSON serializable" % (o,))

    def encode(self, o):
        """
        Return a JSON string representation of a Python data structure.
        """
        # This doesn't pass the iterator directly to ''.join() because it
        # sucks at reporting exceptions.  It's going to do this internally
        # anyway because it uses PySequence_Fast or similar.
        chunks = list(self.iterencode(o))
        return ''.join(chunks)

# emulate poorly named json-py API
def dumps(obj, **kw):
    """
    Return a JSON string representation of a Python data structure using the
    default JSONEncoder.
    """
    return JSONEncoder(**kw).encode(obj)

write = dumps

def dump(obj, fp, **kw):
    for chunk in JSONEncoder(obj, **kw).encode(obj):
        fp.write(chunk)

__all__ = ['JSONEncoder', 'write', 'dump', 'dumps']
