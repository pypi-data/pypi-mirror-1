import sys
import pydoc
import os.path as path
import rst
import pudge

from inspect import *
import warnings

meta_names = ['all', 'author', 'copyright', 'date', 'license', 'revision',
              'version']
meta_names = set(['__%s__' % n for n in meta_names])

# Pydoc may import or look at deprecated things (during the inspection
# process) ; this isn't really a problem, though:
warnings.filterwarnings(
    'ignore', category=DeprecationWarning, module='pydoc')

def ispackage(obj):
    if ismodule(obj) and hasattr(obj, '__file__'):
        file = obj.__file__
        ext = ['.py', '.pyc', '.pyo']
        for e in ext:
            if file.endswith('__init__' + e):
                return 1
    return 0

def qualified_name(obj):
    if ismodule(obj):
        return obj.__name__
    elif isclass(obj) or isfunction(obj):
        return obj.__module__ + '.' + obj.__name__
    elif ismethod(obj):
        return qualified_name(obj.im_class) + obj.func_name

def safe_getmembers(object):
    """Return all members of an object as (name, value) pairs sorted by name.
    
    Unlike inspect.getmembers, this will simply ignore AttributeErrors."""
    results = {}
    for key in dir(object):
        try:
            value = getattr(object, key)
        except AttributeError:
            continue
        results[key] = value
    # We only care about sorting by key here, so ignore value while
    # sorting in case value has a custom __cmp__ method that may
    # infinitely recurse.
    keys = sorted(results.keys())
    results = [(key, results[key]) for key in keys]
    return results


class Browser(object):
    def __init__(self, module_names, exclude_modules):
        self.module_names = module_names
        self.exclude_modules = exclude_modules
        self.cache = {}
    
    def find(self, name, contained=0):
        """
        Locate an object by it's qualified name.

        ``name`` is the qualified name of the package, module, class,
        routine, or data (e.g. 'package.module.Class').
        """
        if contained and not self.is_inside(name):
            return
        cache = self.cache
        assert name, "Name required (not %r)" % name
        # XXX: Was like this, but seems like name should be required
        #if not name:
        #    return None
        if cache.has_key(name):
            return cache[name]
        rslt = None
        if '.' in name:
            components = name.split('.')
            module_name = components[0]
            components = components[1:]
            module = self.find(module_name)
            if module:
                rslt = module.find('.'.join(components))
        else:
            try:
                rslt = Object(name, __import__(name), None, 0, self)
            except ImportError, e:
                pass
        if rslt is None:
            # XXX: Should this be ImportError, NameError, ...?
            # We don't really know what kind of object we are looking for.
            raise ImportError("Module not found: %s" % name)
        cache[name] = rslt
        return rslt
    
    def is_inside(self, name):
        for m in self.module_names:
            if name.startswith(m):
                return 1
    
    def modules(self, recursive=0):
        """Iterate over top level packages and modules."""
        if recursive:
            modules = []
            for m in self.module_names:
                m = self.find(m)
                if m:
                    modules.append(m)
                    for m in m.modules(recursive=1, visible_only=0):
                        modules.append(m)
                # TODO: warn about module not found
            return modules
        else:
            return [self.find(m) for m in self.module_names if m]


def Object(name, obj, parent, module, browser):
    cls = None
    if ismodule(obj):
        cls = ispackage(obj) and Package or Module
    elif isclass(obj):
        cls = Class
    elif isroutine(obj):
        cls = Routine
    elif not (isframe(obj) or istraceback(obj) or iscode(obj)):
        cls = Attribute
    if cls is not None:
        return cls(name, obj, parent, module, browser)


class Name(object):
    
    exclude_members = set(['__doc__', '__dict__'])
    
    def __init__(self, name, obj, parent, module, browser):
        self.name = name
        self.obj = obj
        self.parent = parent
        self.in_module = module
        self.browser = browser
        self._initialize()
    
    
    def relative_file(self, ext='.py'):
        real = self.real_module
        if real:
            relfile = real.__name__.replace('.', '/')
            if ispackage(real):
                relfile += '/__init__'
            if ext:
                relfile += ext
            return relfile
    
    def qualified_name(self):
        names = [self.name]
        p = self.parent
        while p:
            names.insert(0, p.name)
            p = p.parent
        return '.'.join(names)
    
    def moduleless_name(self):
        names = [self.name]
        p = self.parent
        while not p.ismodule():
            names.insert(0, p.name)
            p = p.parent
        return '.'.join(names)
    
    def source_lines(self):
        try:
            (line, code) = getsourcelines(self.obj)
        except (IOError, TypeError):
            pass
        except IndentationError, e:
            raise IndentationError('In module %s: %s' % (
                self.qualified_name(), e))
        except Exception, e:
            e.args += ('in module: %s' % self.qualified_name()),
            raise
        else:
            if isinstance(line, list):
                # XXX work around python bug
                (line, code) = (code, line)
            if code:
                return (line, line + len(code))
        return (0, 0)
    
    def isvisible(self):
        name = self.name
        if name.startswith('__') and name.endswith('__'):
            return 1
        try:
            if getattr(self.obj, '__deprecated__', False):
                return False
        except:
            pass
        try:
            pudge_all = self.parent.obj.__pudge_all__
        except AttributeError:
            pass
        else:
            return name in pudge_all
        try:
            all = self.parent.obj.__all__
        except AttributeError:
            pass
        else:
            return name in all
        if name.startswith('_'):
            return 0
        return not self.isalias()
    
    def ispackage(self):
        return ispackage(self.obj)
    
    def ismodule(self):
        return ismodule(self.obj)
    
    def isclass(self):
        return isclass(self.obj)
    
    def isroutine(self):
        return isroutine(self.obj)
    
    def isdata(self):
        return pydoc.isdata(self.obj)
    
    def isalias(self):
        if self.in_module == 0:
            return 0
        return self.actual_module != self.in_module
    
    def ismeta(self):
        return self.name in meta_names
    
    def hasdoc(self):
        if self.doc(strip=0):
            return 1
    
    def doc(self, strip=1, blurbless=0, html=0):
        if not self.obj:
            return ''
        ds = getattr(self.obj, '__doc__', None)
        if ds and strip:
            ds = rst.trim(ds)
        if ds and blurbless:
            parts = ds.split('\n\n', 1)
            if len(parts) > 1:
                ds = parts[1].strip()
            else:
                return ''
        if ds and html:
            ds = rst.to_html(ds, self.qualified_name())
        return ds or ''
    
    def blurb(self, html=1):
        ds = self.doc()
        if ds:
            parts = ds.split('\n\n')
            ds = parts[0]
        if ds and html:
            try:
                ds = rst.to_html(ds, self.qualified_name()).strip()
            except Exception, e:
                args = list(e.args)
                if not args:
                    args = [None]
                args[0] = '%s (while parsing %s)' % (e, self.qualified_name())
                e.args = tuple(args)
                raise
            if ds.startswith('<p>') and ds.endswith('</p>'):
                ds = ds[3:-4]
        return ds
    
    def html(self, blurbless=0):
        from warnings import warn
        warn("Name.html() is deprecated. Use Name.doc(html=1) instead.",
             DeprecationWarning, stacklevel=2)
        return self.doc(blurbless=blurbless, html=1)
    
    def formatargs(self):
        try:
            (args, varargs, varkw, defaults) = getargspec(self.obj)
        except TypeError:
            return "(...)"
        return formatargspec(args, varargs, varkw, defaults)
    
    def filtered_members(self):
        excludes = self.exclude_members
        for n, v in safe_getmembers(self.obj):
            if n not in excludes:
                yield n, v
    
    def members(self):
        if not hasattr(self, '_members'):
            members = self._load_members()
            self.__dict__['members'] = members
        return members
    members = property(members)
    
    def members_with(self, predicate):
        for m in self.members.values():
            if predicate(m):
                yield m
    
    def members_with_any(self, *predicates):
        predicates = ['is' + p for p in predicates]
        members = self.members.values()
        for m in self.members.values():
            for p in predicates:
                if getattr(m, p)():
                    yield m
                    break
    
    def members_with_all(self, *predicates):
        predicates = ['is' + p for p in predicates]
        members = self.members.values()
        for m in self.members.values():
            for p in predicates:
                if not getattr(m, p)():
                    break
            else:
                yield m
    
    def classes(self, visible_only=1):
        return self.all(visible_only, predicate=lambda m: m.isclass())
    
    def routines(self, visible_only=1):
        return self.all(visible_only, predicate=lambda m: m.isroutine())
    
    def modules(self, visible_only=1, recursive=0, real_modules=None):
        if not real_modules:
            real_modules = set()
        for m in self.all(visible_only, predicate=lambda m: m.ismodule(),
                          exclude_names=self.browser.exclude_modules):
            real_module = m.real_module
            if real_module not in real_modules:
                # Only yield if properly named.
                if m.qualified_name() == real_module.__name__:
                    real_modules.add(real_module)
                    yield m
                    if recursive:
                        for m in m.modules(visible_only, 1,
                                           real_modules=real_modules):
                            real_module = m.real_module
                            if real_module not in real_modules:
                                # Only yield if properly named.
                                if m.qualified_name() == real_module.__name__:
                                    real_modules.add(real_module)
                                    yield m
    
    def attributes(self, visible_only=1, meta=0):
        predicate = lambda m: m.isdata() and (meta or not m.ismeta())
        return self.all(visible_only, predicate)
    
    def all(self, visible_only=1, predicate=None,
            exclude_names=None):
        for m in self.members.values():
            if exclude_names and m.qualified_name() in exclude_names:
                continue
            if (visible_only and not m.isvisible()) or \
               (predicate and not predicate(m)):
                continue
            yield m
    
    def find(self, name):
        parts = name.split('.', 1)
        member_name, rest = parts[0], parts[1:]
        members = self.members
        if members.has_key(member_name):
            member = members[member_name]
            if rest:
                return member.find(rest[0])
            return member
        else:
            pudge.log.debug('%r not found in %r', member_name, self.qualified_name())
    
    def _initialize(self):
        pass
    
    def _load_members(self):
        Object = self._member_object
        members = {}
        for name, value in self.filtered_members():
            member = Object(name, value)
            members[name] = member
        return members
    
    def _member_object(self, name, obj):
        return Object(name, obj, self, self.in_module, self.browser)


class Module(Name):
    exclude_members = Name.exclude_members.union(['__builtins__',
                                                  '__file__',
                                                  '__name__',
                                                  '__path__',
                                                  '__pudge_all__',
                                                  # XXX: Should this be hidden?:
                                                  # (it is for extra doctest tests)
                                                  '__test__'])
    type_name = 'module'
    
    def _initialize(self):
        name = self.obj.__name__
        if '.' in name:
            self.actual_module = sys.modules[name.rsplit('.', 1)[0]]
        else:
            self.actual_module = None
        self.real_module = self.obj    
    
    def _member_object(self, name, obj):
        return Object(name, obj, self, self.obj, self.browser)


class Package(Module):
    
    def _fill_modules_and_packages(self, members):
        object = self.obj
        names = dict(members)
        qname = self.qualified_name()
        from pydoc import safeimport, ispackage
        # XXX: why does this only look at __path__[0]?
        for imp_path in object.__path__:
            for file in os.listdir(imp_path):
                p = path.join(imp_path, file)
                modname = getmodulename(file)
                if modname == '__init__':
                    continue
                if modname and file.endswith('.py') and not file.startswith('.'):
                    if modname in names:
                        value = names[modname]
                        # TODO check that the module is what we expect
                        if not ismodule(value):
                            # TODO: use logging here if possible
                            pudge.log.warn('%s.%s hides module with same name',
                                           qname, modname)
                        continue
                    module = safeimport('%s.%s' % (qname, modname))
                elif ispackage(p):
                    module = safeimport('%s.%s' % (qname, file))
                    modname = file
                else:
                    continue
                members.append((modname, module))
    
    def filtered_members(self):
        sup = super(Package, self)
        members = list(sup.filtered_members())
        self._fill_modules_and_packages(members)
        return members



class Class(Name):
    type_name = 'class'
    
    exclude_members = Name.exclude_members.union(
        ['__class__', '__delattr__', '__getattribute__',
         '__hash__', '__module__', '__new__', '__reduce__',
         '__reduce_ex__', '__repr__', '__setattr__', '__str__',
         '__weakref__', '__metaclass__', '__getattr__',
         '__test__'])
    
    def _initialize(self):
        self.actual_module = sys.modules[self.obj.__module__]
        self.real_module = self.actual_module

class Routine(Name):
    type_name = 'routine'
    def _initialize(self):
        obj = self.obj
        if hasattr(obj, '__module__'):
            # for functions
            look_in = obj
        elif hasattr(obj, 'im_class'):
            # for methods
            look_in = obj.im_class
        elif hasattr(obj, '__objclass__'):
            # for methodwrappers
            look_in = obj.__objclass__
        modname = getattr(look_in, '__module__', None)
        self.actual_module = modname and sys.modules[modname]
        self.real_module = self.actual_module
    
    def ismethod(self):
        return ismethod(self.obj)
    
    def isfunction(self):
        return isfunction(self.obj)
    
    def ismethoddescriptor(self):
        return ismethoddescriptor(self.obj)
    
    def _load_members(self):
        return {}

class Attribute(Name):
    type_name = 'attribute'
    
    def _initialize(self):
        self.actual_module = self.in_module
        self.real_module = self.actual_module
    
    def _load_members(self):
        return {}
    
    def doc(self, strip=1, blurbless=0, html=0):
        if isinstance(self.obj, property) and getattr(self.obj, '__doc__', None):
            return super(Attribute, self).doc(
                strip=strip, blurbless=blurbless, html=html)
        else:
            return ''
