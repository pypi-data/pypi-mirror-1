"""Source enhanced Python object inspection."""

import sys
import os
import os.path as path
import inspect
import types

import pudge.rst as rst
import pudge.scanner as scanner

class MemberError(Exception):
    """
    Raise when an inconsistent class is encountered.

    The most common cause of this exception is when an ``__all__`` attribute
    contains a name that does not exist.
    """
    pass

def find(name, cache=1):
    """
    Locate an object by it's qualified name.
    
    ``name`` is the qualified name of the package, module, class,
    function, or attribute (e.g. 'package.module.Class').
    
    ``cache`` specifies whether the lookup should be stored in the cache.
    This decreases subsequent lookup times significantly but also keeps a
    reference to the loaded object.
    """
    if not name:
        return None
    if find.cache.has_key(name):
        return find.cache[name]
    rslt = None
    if '.' in name:
        components = name.split('.')
        module_name = components[0]
        components = components[1:]
        module = find(module_name)
        if module:
            rslt = module.find('.'.join(components))
    else:
        try:
            rslt = ModulePeruser(name, __import__(name),
                                 None, 0)
        except ImportError:
            pass
    if cache:
        find.cache[name] = rslt
    return rslt

find.cache = {}

class Peruser(object):
    """Object peruser base class.

    Perusers are a sort of special case Python object inspection helper
    that is geared toward inspecting Python objects for the generating
    source code. Perusers use a combination of reflection and source
    scanning.
    
    """

    # Specifies which special members are ignored when generating
    # documentation
    exclude_member_names = set(['__doc__', '__weakref__', '__module__',
                                '__builtins__', '__file__', '__name__',
                                '__version__', '__revision__',
                                '__license__', '__date__', '__author__',
                                '__copyright__', '__metaclass__',
                                '__builtin__'])
    
    def __init__(self, name, obj, parent, private, token=0):
        """Create a Peruser.
        
        Peruser object's shouldn't be instantiated directly. Use the
        `pudge.peruser.find` function to locate objects initially or use
        the `find`, `locate`, `documented_members`, etc. to get at child
        Perusers.
        
        """
        self.obj = obj
        self.name = name
        self.human_name = name
        self.parent = parent
        self.private = private
        self._members = {}
        self._public_members = None
        if token != 0:
            self._token = token
        
    @property
    def public_members(self):
        """Return a sequence of string names containing all public members.

        If source code is available, the names are returned in the order
        they are defined in the source, unless an ``__all__`` atttribute
        is present in which case the order specified by ``__all__``
        takes precedence.

        """
        if self._public_members is None:
            if hasattr(self.obj, '__all__'):
                members = self.obj.__all__[:]
            else:
                members = []
                for name in self.dir():
                    if ((name.startswith('_') and not name.endswith('__'))
                        or name in self.exclude_member_names):
                        continue
                    members.append(name)
                if self.source:
                    source_members = []
                    for child in self.source.children:
                        name = child.name
                        if name in members:
                            members.remove(name)
                            source_members.append(name)
                    members = source_members + members
            self._public_members = members
        return self._public_members

    def source(self):
        """Return the source ``Token`` for this object.

        See `pudge.scanner.Token` for more information on ``Token``
        objects.
        """
        if not hasattr(self, '_token'):
            canonical = self.get_canonical()
            filename = canonical and canonical.get_file()
            if filename is None:
                self._token = None
            else:
                file_token = scanner.scan(filename, cache=1)
                child_name = canonical.get_moduleless_name()
                if child_name:
                    self._token = file_token.find(child_name)
                else:
                    self._token = file_token
        return self._token
    source = property(source, doc=source.__doc__)
    
    def parents(self):
        """Iterate over ancestor ``Peruser`` objects."""
        p = self.parent
        while p:
            yield p
            p = p.parent
    
    def get_actual_module(self):
        """Return the actual module this object belongs to.
        
        The 'actual module' is the module that the object belongs to as
        defined at the source level. The `get_logical_module` method can
        also be used to retrieve the runtime level module the object belongs
        to.
        """ 
        module = getattr(self.obj, '__module__', None)
        return find(module)
    
    def get_actual_file(self):
        """Equivelant to ``get_actual_module().get_file()``"""
        return self.get_actual_module().get_file()
    
    def get_logical_module(self):
        """The 'logical' ModulePeruser that owns this object."""
        p = self
        while p and not isinstance(p, ModulePeruser):
            p = p.parent
        return p
    
    def get_canonical(self):
        """The canonical version of this object."""
        if self.is_canonical():
            return self
        module = self.get_actual_module()
        if module is not None:
            return module.locate(self.obj)
        
    def get_canonical_name(self):
        """Equivelant to ``get_canonical().get_qualified_name()``"""
        canonical = self.get_canonical()
        if canonical is not None:
            return canonical.get_qualified_name()

    def get_canonical_root(self):
        """
        The name of the top level package or module of this object.
        """
        canon = self.get_canonical_name()
        if canon:
            return canon.split('.', 1)[0]

    def is_canonical(self):
        """Was the object defined here or did it get linked in at runtime."""
        if (self.get_actual_module() == self.get_logical_module()):
            source = self.source
        return 
    
    def get_relative_file(self):
        #assert not self.is_alias(), "Only call this on actual objects"
        name  = self.get_logical_module().get_qualified_name().split('.')
        if self.is_package():
            name.append('__init__')
        return path.join(*name) + '.py'
    
    def get_moduleless_name(self):
        """The name of the object not including package or module names"""
        rslt = []
        p = self
        while p and not isinstance(p, ModulePeruser):
            rslt.insert(0, p.name)
            p = p.parent
        return '.'.join(rslt)
    
    def link_parts(self):
        module = self.get_logical_module()
        name = module.get_qualified_name()
        if module is self:
            return [name]
        return [name, self.get_qualified_name()[len(name)+1:]]
    
    def get_file(self):
        """Get the name of the file this object is declared in."""
        return self.get_logical_module().get_file()
    
    def get_qualified_name(self):
        """The 'package.module.Object' style name of the object."""
        rslt = [self.name]
        p = self.parent
        while p:
            rslt.insert(0, p.name)
            p = p.parent
        return '.'.join(rslt)
    
    def get_attributes(self):
        attrs = {}
        hide = ['__doc__', '__all__', '__file__', '__package__', '__name__']
        for name in dir(self.obj):
            if name in hide:
                continue
            if name.startswith('__') and name.endswith('__'):
                value = getattr(self.obj, name)
                if isinstance(value, (str, unicode, int, float)):
                    name = name[2:-2]
                    value = unicode(value)
                    if value.startswith('$') and value.endswith('$'):
                        value = value[1:-1].split(':', 1)[-1]
                    attrs[name] = value
        return attrs
    
    def submodules(self):
        for m in self.documented_members('module'):
            if not m.is_recursive():
                yield m
                for m in m.submodules():
                    yield m

    def documented_members(self, types=None):
        for m in self.members(types):
            if m.has_doc():
                yield m

    def undocumented_members(self, types=None):
        for m in self.members(types):
            if not m.has_doc():
                yield m
    
    def members(self, types=None):
        """Return an iterator over members matching the given criteria."""
        if types is None:
            types= ['module', 'class', 'callable', 'name']
        elif isinstance(types, str):
            types = [types]
        names = self.public_members
        for n in names:
            item = self.member(n)
            if not item.type_name in types:
                continue
            m = item.get_actual_module()
            if not m:
                continue
            canonical_root = item.get_canonical_root()
            if (canonical_root is None or
                canonical_root != self.get_canonical_root()):
                continue
            if item.is_recursive():
                continue
            print '%r [%r]' % (self.get_qualified_name(), n)
            yield item
        
    def locate(self, obj, depth=0):
        children = []
        for m in self.members():
            assert not id(m.obj) == id(self.obj)
            if id(m.obj) == id(obj):
                return m
            else:
                children.append(m)
        for ch in children:
            rslt = ch.locate(obj, depth+1)
            if rslt is not None:
                return rslt

    def find(self, name):
        parts = name.split('.')
        current = self
        for p in parts:
            try:
                current = current.member(p)
            except MemberError:
                return
        return current
        
    def member(self, name):
        return self._load_child(name)
        
    def dir(self):
        rslt = dir(self.obj)
        return rslt

    def has_doc(self):
        return self.obj.__doc__ is not None
    
    def get_doc(self, strip_blurb=1):
        rslt = self.obj.__doc__
        if not rslt:
            return ''
        rslt = rst.trim(rslt)
        if strip_blurb:
            parts = rslt.split('\n\n', 1)
            if len(parts) > 1:
                rslt = parts[1]
            else:
                rslt = ''
        return rslt
        
    def get_html_doc(self, strip_blurb=1):
        doc = self.get_doc(strip_blurb)
        return doc and rst.to_html(doc) or ''
    
    def get_blurb(self):
        doc = self.get_doc(strip_blurb=0)
        parts = doc.split('\n\n')
        return parts[0]

    def get_html_blurb(self):
        blurb = self.get_blurb()
        if blurb:
            blurb = rst.to_html(blurb)[3:-5] # removes the <p></p>
        return blurb
    
    def is_package(self):
        return 0
    
    def _load_child(self, name):
        if self._members.has_key(name):
            return self._members[name]
        private = name not in self.public_members
        try:
            obj = getattr(self.obj, name)
        except AttributeError:
            raise MemberError("%s does not contain member: %r"
                              % (self.get_qualified_name(), name))
        C = get_peruser_type(obj)
        token = self.source and self.source.find(name) or 0
        rslt = C(name, obj, self, private, token=token)
        self._members[name] = rslt
        return rslt

    def is_recursive(self):
        obj = self.obj
        for p in self.parents():
            if id(p.obj) == id(obj):
                return 1

    def __repr__(self):
        return '<%s(%r)>' % (self.__class__.__name__, self.get_qualified_name())
        
class ModulePeruser(Peruser):
    """Concrete Peruser implementation for module objects."""
    
    type_name = 'module'

    def __init__(self, name, obj, parent, private, token=0):
        super(ModulePeruser, self).__init__(name, obj, parent, private, token)
        self.link = self.get_qualified_name() + '.html'
    
    def get_canonical(self):
        return self.get_actual_module()
    
    def get_actual_module(self):
        return find(self.obj.__name__)
    
    def get_file(self):
        if hasattr(self.obj, '__file__'):
            return fix_file(self.obj.__file__)
        else:
            return None
        
    def generate(self, dest_dir, source=1, force=0):
        if not path.exists(dest_dir):
            os.makedirs(dest_dir)

    def is_package(self):
        if hasattr(self.obj, '__file__'):
            return self.obj.__file__.endswith('__init__.py') or \
                   self.obj.__file__[0:-1].endswith('__init__.py')
            
    def dir(self):
        rslt = super(ModulePeruser, self).dir()
        if self.is_package():
            package_dir = path.dirname(self.obj.__file__)
            for name in os.listdir(package_dir):
                if path.exists(path.join(package_dir, name, '__init__.py')):
                    if name not in rslt:
                        rslt.append(name)
                elif name.endswith('.py'):
                    name = name[0:-3]
                    if name not in rslt:
                        rslt.append(name)
        return rslt
    
    def check_all_attribute(self):
        try:
            all = getattr(self.obj, '__all__')
        except AttributeError:
            pass
        else:
            for name in all:
                if not isinstance(name, (str, unicode)):
                    yield "%s.__all__ contains a non-string: %r?" \
                          % (self.get_qualified_name(), name)
                if not hasattr(self.obj, name):
                    yield "%s.__all__ has %r but hasattr(%s, %r) disagrees."\
                          % ((self.get_qualified_name(),
                             name) * 2) # :)
        
    def _load_child(self, name):
        try:
            return super(ModulePeruser, self)._load_child(name)
        except MemberError, e:
            # try again after importing
            parts = self.obj.__name__.split('.')
            parts.append(name)
            try:
                m = __import__('.'.join(parts))
            except ImportError:
                #raise MemberError, '.'.join(parts)
                setattr(self.obj, name, None)
            return super(ModulePeruser, self)._load_child(name)


class ClassPeruser(Peruser):
    """Concrete Peruser implementation for class objects."""
    type_name = 'class'

    def __init__(self, name, obj, parent, private, token=0):
        super(ClassPeruser, self).__init__(name, obj, parent, private, token)
        self.link = self.get_qualified_name() + '.html'
    
    def dir(self):
        ls = self.obj.__dict__.keys()
        ls.sort()
        return ls
    
    def format_arg_spec(self):
        if hasattr(self.obj, '__init__'):
            return self.member('__init__').format_arg_spec()
        else:
            return '()'
    
class CallablePeruser(Peruser):
    """Concrete Peruser implementation for functions and methods."""
    type_name = 'callable'

    def __init__(self, name, obj, parent, private, token=0):
        super(CallablePeruser, self).__init__(name, obj, parent, private, token)
        p = self.parent
        self.link = '%s#%s' % (p.link, self.name)
        
    def get_actual_module(self):
        actual = super(CallablePeruser, self).get_actual_module()
        if actual is None:
            if hasattr(self.obj, 'im_class'):
                cls = self.obj.im_class
                return find(cls.__module__)
            else:
                print "actual: %r" % self.get_qualified_name()
                print '  %r' % dir(self.obj)
        return actual
    
    def get_public(self):
        return []
    
    def format_arg_spec(self):
        return format_arg_spec(self.obj)

    def dir(self):
        return []
    
class NamePeruser(Peruser):
    """Concrete Peruser implementation for attributes."""
    type_name = 'name'

    def __init__(self, name, obj, parent, private, token=0):
        super(NamePeruser, self).__init__(name, obj, parent, private, token)
        p = self.parent
        self.link = '%s#%s' % (p.link, self.name)
    
    def get_file(self):
        return self.parent.get_file()
    
    def get_public(self):
        return []

    def get_doc(self, strip_blurb=1):
        return ''

    def get_actual_module(self):
        return self.get_logical_module()

    def dir(self):
        return []
    
peruser_types = [(lambda o: isinstance(o, types.ModuleType),
                    ModulePeruser),
                 (lambda o: isinstance(o, (types.ClassType, types.TypeType)),
                    ClassPeruser),
                 (lambda o: callable(o),
                    CallablePeruser),
                 (lambda o: 1,
                    NamePeruser)]

def get_peruser_type(obj):
    for t, cls in peruser_types:
        if t(obj):
            return cls

def fix_file(name):
    if name.endswith('.pyc') or name.endswith('.pyo'):
        return name[0:-1]
    return name

def format_arg_spec(obj):
    try:
        (args, varargs, varkw, defaults) = inspect.getargspec(obj)
    except TypeError:
        return "(...)"
    rslt = ['(']
    pos = 0
    positional_arg_count = len(args) - len(defaults or [])
    for name in args:
        if pos > 0:
            rslt.append(', ')
        rslt.append(name)
        default_pos = pos - positional_arg_count
        if default_pos >= 0:
            rslt.append('=')
            value = defaults[default_pos]
            rslt.append(repr(defaults[default_pos]))
        pos+=1
    rslt.append(')')
    return ''.join(rslt)

__all__ = ['find',
           'Peruser',
           'ModulePeruser', 'ClassPeruser', 'CallablePeruser', 'NamePeruser']

# module attributes    
__author__ = "Ryan Tomayko <rtomayko@gmail.com>"
__date__ = "$Date: 2005-06-25 18:39:35 -0700 (Sat, 25 Jun 2005) $"
__revision__ = "$Revision: 35 $"
__url__ = "$URL: svn://lesscode.org/pudge/trunk/pudge/peruser.py $"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
