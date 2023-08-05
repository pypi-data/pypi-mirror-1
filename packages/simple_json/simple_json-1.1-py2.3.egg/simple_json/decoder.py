#!/usr/bin/env python
import re

from simple_json.scanner import Scanner, pattern

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

def _floatconstants():
    import struct
    import sys
    _BYTES = '7FF80000000000007FF0000000000000'.decode('hex')
    if sys.byteorder != 'big':
        _BYTES = _BYTES[:8][::-1] + _BYTES[8:][::-1]
    nan, inf = struct.unpack('dd', _BYTES)
    return nan, inf, -inf

NaN, PosInf, NegInf = _floatconstants()

def errmsg(msg, doc, pos):
    lineno = doc.count('\n', 0, pos) + 1
    if lineno == 1:
        colno = pos
    else:
        colno = pos - doc.rindex('\n', 0, pos)
    return '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)

def JSONInfinity(match, context):
    return PosInf, None
pattern('Infinity')(JSONInfinity)

def JSONNegInfinity(match, context):
    return NegInf, None
pattern('-Infinity')(JSONNegInfinity)

def JSONNaN(match, context):
    return NaN, None
pattern('NaN')(JSONNaN)

def JSONTrue(match, context):
    return True, None
pattern('true')(JSONTrue)

def JSONFalse(match, context):
    return False, None
pattern('false')(JSONFalse)

def JSONNull(match, context):
    return None, None
pattern('null')(JSONNull)

def JSONNumber(match, context):
    match = JSONNumber.regex.match(match.string, *match.span())
    integer, frac, exp = match.groups()
    if frac or exp:
        res = float(integer + (frac or '') + (exp or ''))
    else:
        res = int(integer)
    return res, None
pattern(r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?')(JSONNumber)

STRINGCHUNK = re.compile(r'("|\\|[^"\\]+)', FLAGS)
STRINGBACKSLASH = re.compile(r'([\\/bfnrt"]|u[A-Fa-f0-9]{4})', FLAGS)
BACKSLASH = {
    '"': u'"', '\\': u'\\', '/': u'/',
    'b': u'\b', 'f': u'\f', 'n': u'\n', 'r': u'\r', 't': u'\t',
}

DEFAULT_ENCODING = "utf-8"

def scanstring(s, end, encoding=None):
    if encoding is None:
        encoding = DEFAULT_ENCODING
    chunks = []
    while 1:
        chunk = STRINGCHUNK.match(s, end)
        end = chunk.end()
        m = chunk.group(1)
        if m == '"':
            break
        if m == '\\':
            chunk = STRINGBACKSLASH.match(s, end)
            if chunk is None:
                raise ValueError(errmsg("Invalid \\escape", s, end))
            end = chunk.end()
            esc = chunk.group(1)
            try:
                m = BACKSLASH[esc]
            except KeyError:
                m = unichr(int(esc[1:], 16))
        if not isinstance(m, unicode):
            m = unicode(m, encoding)
        chunks.append(m)
    return u''.join(chunks), end

def JSONString(match, context):
    encoding = getattr(context, 'encoding', None)
    return scanstring(match.string, match.end(), encoding)
pattern(r'"')(JSONString)

WHITESPACE = re.compile(r'\s+', FLAGS)

def skipwhitespace(s, end):
    m = WHITESPACE.match(s, end)
    if m is not None:
        return m.end()
    return end

def JSONObject(match, context):
    pairs = {}
    s = match.string
    end = skipwhitespace(s, match.end())
    nextchar = s[end:end + 1]
    # trivial empty object
    if nextchar == '}':
        return pairs, end + 1
    if nextchar != '"':
        raise ValueError(errmsg("Expecting property name", s, end))
    end += 1
    encoding = getattr(context, 'encoding', None)
    while True:
        key, end = scanstring(s, end, encoding)
        end = skipwhitespace(s, end)
        if s[end:end + 1] != ':':
            raise ValueError(errmsg("Expecting : delimiter", s, end))
        end = skipwhitespace(s, end + 1)
        try:
            value, end = JSONScanner.iterscan(s, idx=end).next()
        except StopIteration:
            raise ValueError(errmsg("Expecting object", s, end))
        pairs[key] = value
        end = skipwhitespace(s, end)
        nextchar = s[end:end + 1]
        end += 1
        if nextchar == '}':
            break
        if nextchar != ',':
            raise ValueError(errmsg("Expecting , delimiter", s, end - 1))
        end = skipwhitespace(s, end)
        nextchar = s[end:end + 1]
        end += 1
        if nextchar != '"':
            raise ValueError(errmsg("Expecting property name", s, end - 1))
    return pairs, end
pattern(r'{')(JSONObject)
            
def JSONArray(match, context):
    values = []
    s = match.string
    end = skipwhitespace(s, match.end())
    # look-ahead for trivial empty array
    nextchar = s[end:end + 1]
    if nextchar == ']':
        return values, end + 1
    while True:
        try:
            value, end = JSONScanner.iterscan(s, idx=end).next()
        except StopIteration:
            raise ValueError(errmsg("Expecting object", s, end))
        values.append(value)
        end = skipwhitespace(s, end)
        nextchar = s[end:end + 1]
        end += 1
        if nextchar == ']':
            break
        if nextchar != ',':
            raise ValueError(errmsg("Expecting , delimiter", s, end))
        end = skipwhitespace(s, end)
    return values, end
pattern(r'\[')(JSONArray)
 
ANYTHING = [
    JSONTrue,
    JSONFalse,
    JSONNull,
    JSONNaN,
    JSONInfinity,
    JSONNegInfinity,
    JSONNumber,
    JSONString,
    JSONArray,
    JSONObject,
]

JSONScanner = Scanner(ANYTHING)

class JSONDecoder(object):
    """
    Simple JSON <http://json.org> decoder to Python data structures.

    Performs the following translations in decoding
    
    - null -> None
    - true -> True
    - false -> False
    - Number (integer) -> int
    - Number (real) -> float
    - String -> unicode
    - Object -> dict
    - Array -> list

    It also understands NaN, Infinity, and -Infinity as float values, which
    is outside the JSON spec.
    """
    def __init__(self, encoding=None):
        self.encoding = encoding

    def raw_decode(self, s, **kw):
        kw.setdefault('context', self)
        try:
            obj, end = JSONScanner.iterscan(s, **kw).next()
        except StopIteration:
            raise ValueError("No JSON object could be decoded")
        return obj, end

    def decode(self, s):
        obj, end = self.raw_decode(s, idx=skipwhitespace(s, 0))
        end = skipwhitespace(s, end)
        if end != len(s):
            raise ValueError(errmsg("Extra data", s, end))
        return obj

def loads(obj, **kw):
    """
    Return a JSON string representation of a Python data structure using the
    default JSONEncoder.
    """
    return JSONDecoder(**kw).decode(obj)

# emulate poorly named json-py API
read = loads

def load(fp, **kw):
    return loads(fp.read(), **kw)

__all__ = ['JSONDecoder', 'read', 'load', 'loads']
