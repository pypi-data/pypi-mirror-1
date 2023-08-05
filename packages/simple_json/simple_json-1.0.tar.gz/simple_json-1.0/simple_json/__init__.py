r"""
A simple, fast, extensible JSON encoder and decoder for Python::

    >>> import simple_json
    >>> simple_json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
    '["foo", {"bar":["baz", null, 1.0, 2]}]'
    >>> simple_json.loads(_)
    [u'foo', {u'bar': [u'baz', None, 1.0, 2]}]
    >>> print simple_json.dumps("\"foo\bar")
    "\"foo\bar"
    >>> simple_json.loads('"\\"foo\\bar"')
    u'"foo\x08ar'
    >>> print simple_json.dumps(u'\u1234')
    "\u1234"
    >>> print simple_json.dumps('\\')
    "\\"
    >>> from StringIO import StringIO
    >>> io = StringIO()
    >>> simple_json.dump(['streaming API'], io)
    >>> io.getvalue()
    '["streaming API"]'
    >>> io.seek(0)
    >>> simple_json.load(io)
    [u'streaming API']
    >>> try: # sludge to make the doctest work on Python 2.3
    ...     (set, frozenset) and None
    ... except NameError:
    ...     from sets import Set as set, ImmutableSet as frozenset
    >>> class SetEncoder(simple_json.JSONEncoder):
    ...     def default(self, obj):
    ...         if isinstance(obj, (set, frozenset)):
    ...             return list(obj)
    ...         return JSONEncoder.default(self, obj)
    ... 
    >>> SetEncoder().encode(set([1, 2, 3, 4]))
    '[1, 2, 3, 4]'
    >>> simple_json.loads(_)
    [1, 2, 3, 4]
    >>> list(SetEncoder().iterencode(set(["foo", "bar"])))
    ['[', '"foo"', ', ', '"bar"', ']']
    

Note that the JSON produced by this module is a subset of YAML,
so it may be used as a serializer for that as well.

See the docstrings in simple_json.encoder and simple_json.decoder
for more information.
"""
__version__ = '1.0'
from encoder import *
from decoder import *
