"""A rudamentary Python source code scanner.

A regular expression based Python source code scanner. The `scan`
function runs through a file line by line and collects bits of
information not provided by object introspection.

Synopsis
--------

Consider the following source file (``example.py``):

>>> foo = 'FOO'
>>> def bar_function():
...     print foo
>>> class Bling:
...     foo = 'Bling\'s FOO'
...     def bar_method(self):
...         print self.foo

The `scan` function returns a `Token` instance representing the file
that was scanned:

>>> import pudge.scanner as scanner
>>> file_tok = scanner.scan('example.py')
>>> (file_tok.type, file_tok.name)
('file', 'example.py')

Traverse the token tree using `Token.find`:

>>> tok = file_tok.find('foo')
>>> (tok.type, tok.name, tok.line, tok.last_line)
('=', 'foo', 1, 2)

Line numbers are one piece of information not available via introspection.

You can traverse multiple levels of depth using dot notation:

>>> tok = file_tok.find('Bling.bar_method')
>>> (tok.type, tok.name, tok.line, tok.last_line)
('def', 'bar_method', 6, 8)

`Token` instances can be treated like dictionaries for syntactic
pleasure; this is just like calling find:

>>> tok = file_tok['Bling']
>>> (tok.type, tok.name, tok.children)
('class', 'Bling', [<Token('=', 'foo')>, <Token('def', 'bar_method')>]) 

Note also that the `Token.children` attribute contains a ``list`` containing
the immediately children of the token. This provides a source level order of
tokens which is not available via introspection.

"""

import re

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Token(object):
    """A Python syntax token.

    This class provides access to information about a named python object.
    Token objects are arranged into a hierarchy that *should* look exactly
    like the introspection object hierarchy.

    Token objects have six important attributes:

    * ``type`` - The token's type.
      This will be one of the following string values:
      
      * ``'file'`` - The token is a root file token. The `name` attribute
        contains the name of the file.
      * ``'def'`` - The token describes a function or method.
      * ``'class'`` - The token describes a class.
      * ``'='`` - The token describes an attribute
      
    * ``name`` - The name of the file, class, function, or attribute
     
    * ``indent`` - The indent level as an integer starting at ``0``.

    * ``line`` - The line number that the token appears on.
    
    * ``last_line`` - The line at which the token is no longer 'on the stack'

    * ``children`` - ``list`` of child tokens.
    
    """
    def __init__(self, type, name, line, indent):
        self.type = type
        self.name = name
        self.indent = indent
        self.line  = line
        self.last_line = None
        self.children = []

    def tuplize(self):
        return (self.type, self.name, self.indent, self.line, self.last_line,
                [ch.tuplize() for ch in self.children if self.children])

    def find(self, name):
        components = name.split('.', 1)
        this = components[0]
        for c in self.children:
            if c.name == this:
                if len(components) > 1:
                    return c.find(components[1])
                else:
                    return c
        return None

    def for_line(self, line):
        for c in self.children:
            if c.line == line:
                if len(components) > 1:
                    return c.find(components[1])
                else:
                    return c
        return None
    
    def __getitem__(self, name):
        rslt = self.find(name)
        if not rslt:
            raise KeyError(name)
        return rslt
    
    def __iter__(self):
        return iter(self.children)
    
    def __repr__(self):
        return '<Token(%r, %r)>' % (self.type, self.name)

token_patterns = [('def', re.compile(r'[ ]*def\s+([A-Za-z0-9_]+)\s*\(')),
                  ('class', re.compile(r'[ ]*class\s+([A-Za-z0-9_]+)')),
                  ('=', re.compile(r'[ ]*([A-Za-z0-9_]+)\s*=.*'))]

space = re.compile(r'([ ]*)')
_cache = {}

def empty_cache():
    """Empties the ``filename -> Token`` cache.

    It isn't a bad idea to do this every once in a while if you use the
    cache argument to `scan` so that the garbage collector can free up the
    objects.
    """
    global _cache
    _cache = {}

def scan(filename, file=None, cache=0):
    """Scan a file and return collected bits
    
    `filename` is the name of the file to scan. If `file` is specified,
    it is a file object that responds to the ``readline`` method. When a
    truthful `cache` argument is provided, this method memoizes the
    result based on the `filename` argument. *The cache is not thread safe.*

    A single `Token` object is returned that represents the root of the
    tree. The `Token`'s type will be ``'file'``
    """
    # fast path:
    if _cache.has_key(filename):
        return _cache[filename]
    if file is None:
        file = open(filename, 'r')
    current = top = Token('file', filename, 0, -1)
    parents = []
    pos = 0
    indent = 0
    line = file.readline()
    while line:
        pos+=1
        stripped = line.strip()
        if stripped == '' or stripped.startswith('#'):
            line = file.readline()
            continue
        indent = len(space.match(line).group(1)) / 4
        while indent <= current.indent:
            current.last_line = pos
            current = parents.pop()
        if current.type in ['class', 'file'] and indent == current.indent + 1:
            for (t, p) in token_patterns:
                m = p.match(line)
                if m:
                    parents.append(current)
                    current = Token(t, m.group(1), pos, indent)
                    parents[-1].children.append(current)
        line = file.readline()
    for tok in [top] + parents:
        tok.last_line = pos
    if cache:
        _cache[filename] = top
    return top

__all__ = ['scan', 'Token', 'empty_cache', 'token_patterns']

# module attributes    
__author__ = "Ryan Tomayko <rtomayko@gmail.com>"
__date__ = "$Date: 2005-05-25 23:16:24 -0400 (Wed, 25 May 2005) $"
__revision__ = "$Revision: 35 $"
__url__ = "$URL: svn://lesscode.org/pudge/trunk/pudge/scanner.py $"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
