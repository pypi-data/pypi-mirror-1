"""
Plain text Python built-in objects persistence

miniconf provides data persistence of a subset of Python built-in
objects as plain text. Objects are loaded from, and dumped to valid
Python source composed of assignment statements of the form
\"identifier = value\". Supported objects are:

- dictionaries
- lists and tuples
- integers and floats
- plain and unicode strings
- booleans
- None

Arbitrarily complex objects composed of these types can be
handled. miniconf is restricted to these types because they can be
easily reconstructed from literal representation in Python, entirely
known at byte-compilation, without the need to execute the code.

miniconf aims at providing an easy, elegant way to store (dump) and
retrieve (load) configuration information and simple datasets in a
human-readable, familiar pythonic notation, while preventing unwanted
injection of external code.

Usage example
=============

# Load the objects from a textual representation
#
>>> import miniconf
>>> snippet = 'spam = [ 1, True, (\"test\", None) ]; egg = -2'
>>> config = miniconf.load(snippet)
>>> print config
{'egg': -2, 'spam': [1, True, ('test', None)]}

# Note that config could as well be constructed from snippet by doing:
#
>>> config = {}
>>> exec snippet in config
>>> del config['__builtins__']

The whole point of using miniconf instead of the exec statement is
that it is safer, since no arbitrary code execution ever occurs: the
code is only parsed, not executed, and the objects are reconstructed
from the snippet abstract syntax tree. In practice, it makes user
access to simple pythonic data structure possible without having to
fear injection of unwanted third-party code.

# Modify the data and dump it back
#
>>> config['egg'] = u'new_value'
>>> config['new'] = range(10)
>>> print miniconf.dump(config)
egg = u'new_value'

new = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

spam = [1, True, ('test', None)]

Special explanation on pedantry
===============================

All load(), dump() have two modes of operation: pedantic and
non-pedantic.

- On load, the pedantic argument indicates whether the function should
  bail out on un-loadable constructs instead or just ignore
  them. Default is not to be pedantic on load.

- On dump, the pedantic argument indicates if the function should bail
  out when dumping objects that could only be partially restored later
  on (because they belong to a derivate class of a supported type). A
  successfully dump will always be re-loadable anyway regardless of the
  pedantry. Default is to be pedantic on dump.

Please keep in mind that a non-pedantic load or dump does not ensure
that the operation will not raise an exception (such as a SyntaxError
because of an unparsable buffer during a load), only that the level of
tolerance to the minor problems just described will be greater.

Limitations
===========

miniconf has a few limitations one should be aware of:

- It only supports a subset of built-ins types (see above).
  
- It is strictly string-based: it loads from them, and dumps to
  them. Potential race conditions with the underlying sources and
  destinations such as real files has to be dealt with externally
  (handling locks, etc.).

- dump() and load() are not inverse functions, because load() is not
  injective; any special content or formatting in the source code
  (comments, un-loadable objects, non-assignments statements, lexical
  format) will be discarded at load time. See for instance:

  >>> from miniconf import load, dump
  >>> print dump(load('spam = \"egg\" # this comment will be lost'))
  spam = 'egg'

  Basically, this means that an external agent (user or application)
  cannot add an element such as a comment to a snippet, and have it
  preserved next time the program will have loaded, then dumped it
  back. Of course, one can very well choose not to systematically dump
  the data over the source of the next load, which alleviates this
  limitation.

"""
# Written by Sylvain Fourmanoit <syfou@users.sourceforge.net>, 2006.
# Please carbon-copy any comment or bug report to this address.

import compiler
import re
import pprint
import textwrap

class _Load:
    names = {'None': None, 'True': True, 'False': False}
    
    def __init__(self):
        if not hasattr(_Load, 'lookup'):
            _Load.lookup = dict([(item[5:], getattr(_Load, item))
                                 for item in _Load.__dict__
                                 if '_node' == item[:5]])
            
    def __call__(self, buf, pedantic):
        # We use the supplemented compiler interface to the parser
        # module because it comes with a DOM-like interface very
        # handy for "walking" the tree.
        self.pedantic = pedantic 
        return dict(self._group(
            self.start_walk(compiler.parse(buf).getChildNodes()[0])))
    
    def start_walk(self, node):
        assert(node.__class__ == compiler.ast.Stmt)
        for child in node.getChildNodes():
            for result in self.walk(child):
                yield result
                    
    def walk(self, node):
        try:
            return self.lookup[node.__class__.__name__](self, node)
        except KeyError:
            return self._nodeDiscard(node)

    def assert_complex(self, node):
        if isinstance(node.value, complex):
            raise TypeError('complex numbers are not supported')

    def _nodeAssign(self,node):
        return (self.walk(node.getChildNodes()[0]),\
                self.walk(node.getChildNodes()[1]))
        
    def _nodeAssName(self, node):
        return node.name
        
    def _nodeConst(self, node):
        self.assert_complex(node)
        return node.value

    def _nodeUnarySub(self, node):
        node = node.getChildNodes()[0]
        self.assert_complex(node)
        return -(node.value)
        
    def _nodeName(self, node):
        try:
            return self.names[node.name]
        except KeyError:
            if self.pedantic:
                raise TypeError('name node with value "%s" discarded' %
                                node.name)
            else:
                return []
        
    def _nodeDict(self, node):
        return dict([(self.walk(k),self.walk(v))
                     for k,v in node.items])

    def _nodeTuple(self, node):
        return tuple([self.walk(i)
                      for i in node.nodes])

    def _nodeList(self, node):
        return [self.walk(i)
                for i in node.nodes]

    def _nodeDiscard(self, node):
        if self.pedantic:
            raise TypeError('node of type "%s" discarded' % \
                            node.__class__.__name__)
        return []

    def _group(self, iterable):
        group=[]
        for item in iterable:
            group.append(item)
            if len(group)==2:
                yield group
                group=[]

class _Dump:
    types = (dict, list, tuple, int, float, str, unicode, bool, type(None))
        
    def __init__(self):
        self.hexpr = re.compile('^[^#]', re.MULTILINE)
            
    def __call__(self, data, headers, pedantic, **kw):
        data = self.recast(data, pedantic, [dict])
        return '\n'.join(
            [self.header(headers, '--top--', **kw)] +
            ['%s%s = %s\n' %
             (self.header(headers, k, **kw),
              k, pprint.pformat(data[k], **kw))
             for k in self.keys(data)] +
            [self.header(headers, '--bottom--', **kw)]
            ).strip()
        
    def recast(self, data, pedantic, types):
        # This makes sure that the data object is only aggregated
        # from supported types; if pedantic is False, it even
        # coerce every sub-objects to supported base types, to make
        # sure that the final representation will be pretty-printed
        # to something that will always be loadable later on.
        def cast(data, pedantic, types):
            if pedantic:
                if type(data) in types:
                    return data
            else:
                for t in types:
                    if isinstance(data, t):
                        if t is not type(None):
                            return t(data)
                        else:
                            return None

            raise TypeError( \
         'Object "%s" is of unsupported type %s, while it should be one of %s' %
         (data, type(data), types))

        data = cast(data, pedantic, types)
            
        if type(data) is dict:
            iterator = data.iteritems()
        elif type(data) in (list, tuple):
            iterator = iter(data)
        else:
            iterator = None

        if iterator is not None:
            return type(data)([self.recast(item, pedantic, self.types)
                               for item in iterator])
        else:
            return data

    def keys(self, data):
        # Order the keys, and make sure that they are all valid
        # Python identifiers.
        ident = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
        keys = data.keys()
        keys.sort()
        for key in keys:
            if not ident.match(key):
                    raise ValueError(
                        'Key "%s" is not a valid Python identifier' % key)
        return keys
 
    def header(self, headers, key, width=80, **kw):
        if headers.has_key(key):
            if type(headers[key]) is str:
                if self.hexpr.search(headers[key]):
                    return format_header(headers[key], width=width) + '\n'
                else:
                    return headers[key] + '\n'
            else:
                raise TypeError( \
                    'Header for identifier "%s" is of type "%s", not string' % \
                    (key, type(headers[key])))
        else:
            return ''

def format_header(header, width=80, **kw):
    """
    Transform a string into a python comment.
    
    Turn header into a valid Python comment by prepending '# ' to each
    line, and wrap it to the given width. Return the result as a
    single, potentially multi-lines string.
    """
    width -= 2
    return '\n'.join(['# ' + line
                      for line in textwrap.wrap(header, width)])

def load(buf, pedantic=False):
    """
    Load configuration from string, returning a dictionary.

    Load configuration from string buf. If pedantic is True,
    un-loadable elements will raise TypeError exceptions instead of
    being silently dropped. On success, return a dictionary containing
    the parsed built-in objects, indexed by assignment names. On
    error, raise a SyntaxError, TypeError or ValueError exception.
    """
    return _Load()(buf, pedantic)

def unrepr(buf, pedantic=False):
    """
    Return an object from its canonical string representation, buf.

    This is a specialized version of load() operating on the canonical
    representation of a single value instead than on a sequence of
    assignment statements. This should never fail on any possible
    values of data where data only includes supported types (see
    above):

    >>> assert(data == unrepr(repr(data)))

    The pedantic argument has the same meaning than for load(). On
    error, it can raise a SyntaxError, TypeError or ValueError
    exception.
    """

    # Let's reuse the same interface than for load: it is somewhat
    # suboptimal, but cleaner.
    return _Load()('data = %s' % buf, pedantic)['data']

def dump(data, comments={}, pedantic=True, **kw):
    """
    Dump configuration from dictionary, returning a string.

    Dump configuration from dictionary data, prepending string
    comments from corresponding values (i.e. associated to the
    matching keys in data) in comments. If pedantic is True, a
    TypeError exception will be raised if some value in data is a
    derivate class of an otherwise supported type. Return the
    formatted string on success, or raise a TypeError or ValueError on
    error. data dictionary is dumped in identifiers' alphabetical
    order. Valid keywords are optional arguments to the low-level
    PrettyPrinter object (see the pformat method from the pprint
    module).

    === Note on comments ===

    If every lines in a comment string are already starting with a
    pound sign ('#') thus making the string an already valid Python
    comment, such string is preserved untouched in the output. If not,
    the comment string will be formatted using format_header(), using
    the same width used by the PrettyPrinter. Basically, this means
    you are free to either have comments automatically formatted and
    wrapped as a single paragraph, or use your own layout if you want,
    as long as the whole string keeps being a valid Python comment.

    Values associated with special '--top--' and '--bottom--' keys, if
    they exist in comments, will be respectively included at the
    beginning and end of the return string; same formatting
    rules apply to them.
    """
    return _Dump()(data, headers=comments, pedantic=pedantic, **kw)

