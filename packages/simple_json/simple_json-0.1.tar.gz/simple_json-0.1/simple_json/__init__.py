"""
A simple, fast, extensible JSON encoder for Python::

    >>> import simple_json
    >>> simple_json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
    '["foo", {"bar":["baz", null, 1.0, 2]}]'
    >>> from StringIO import StringIO
    >>> io = StringIO()
    >>> simple_json.dump(['streaming API'])
    >>> io.getvalue()
    '["streaming API"]'
    >>> class SetEncoder(simple_json.JSONEncoder):
    ...     def default(self, obj):
    ...         if isinstance(obj, (set, frozenset)):
    ...             return list(obj)
    ...         return JSONEncoder.default(self, obj)
    ... 
    >>> SetEncoder().encode(set([1, 2, 3, 4]))
    '[1, 2, 3, 4]'
    >>> list(SetEncoder().iterencode(set(["foo", "bar"])))
    ['[', '"foo"', ', ', '"bar"', ']']

Note that the JSON produced by this module is a subset of YAML,
so it may be used as a serializer for that as well.

See the docstrings in simple_json.encoder for more information.
"""
__version__ = '0.1'
from encoder import *
