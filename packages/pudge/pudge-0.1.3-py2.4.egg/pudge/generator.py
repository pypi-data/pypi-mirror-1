"""
Generate Python documentation and other stuff.


"""

import sys
import os
import os.path as path
import stat
import inspect
import time
import kid

import pudge
import pudge.browser as browser
import pudge.colorizer as colorizer
import pudge.rst as rst

from pkg_resources import resource_filename

class Generator(object):
    """
    Takes configuration options and performs file generation.
    """
    
    file_extension = '.html'
    title = 'Project Name'
    dest = '.'
    force = 1
    modules = []
    document_files = []
    xhtml = 0
    fragment = 0
    trac_url = None
    trac_links = [('wiki', 'wiki', 'Collaborative documentation'),
                  ('repository', 'browser', 'Browse subversion repository'),
                  ('roadmap', 'roadmap', 'View the project roadmap'),
                  ('feedback!', 'newticket', 'Report an issue / request an enhancement')]
    mailing_list_url = None
    organization = None
    organization_name = None
    organization_url = None
    blog_url = None
    syndication_url = None
    template_dir = None
    theme = None
    highlighter = 'dbcodeblock'
    stages = ['copy', 'docs', 'index', 'reference', 'source']
    doc_base = None
    exclude_modules = []
    license = None
    profile = False
    
    def __init__(self, modules=None, dest='.', force=1):
        self.modules = modules or []
        self.dest = dest
        self.force = force
        self.settings = {}
        
    def _prepare(self):
        from os.path import join
        template_base = resource_filename(__name__, 'template')
        templates = []
        templates.insert(0, join(template_base, 'base'))
        if self.theme:
            templates.insert(0, join(template_base, self.theme))
        if self.template_dir:
            templates.insert(0, self.template_dir)
        for t in reversed(templates):
            kid.path.insert(t)
        self.templates = templates
        self._template_cache = {}
        self.profile_info = []

    def generate(self):
        self._prepare()
        if self.highlighter == 'dpcodeblock':
            import dpcodeblocksupport
        elif self.highlighter == 'pygments':
            import pygmentsupport
        
        if 'copy' in self.stages:
            self.time_func(None, self.copy_files)
        if 'docs' in self.stages:
            self.time_func(None, self.load_documents)
            self.time_func(None, self.generate_documents)
        if 'index' in self.stages:
            if 'docs' not in self.stages:
                self.time_func(None, self.load_documents)
            self.time_func(None, self.generate_index)
        if 'reference' in self.stages:
            if self.profile > 1:
                import pkg_resources
                pkg_resources.require('Paste')
                from paste.debug.profile import profile_decorator
                profiled = profile_decorator()(self.generate_modules)
            else:
                profiled = self.generate_modules
            self.time_func(None, profiled)
        if 'source' in self.stages:
            self.time_func(None, self.generate_source)
        self.print_profile_info()

    def print_profile_info(self):
        if self.profile:
            print 'Profiling information:'
        for info in self.profile_info:
            print info
    
    def get_template(self, name):
        Template = self._template_cache.get(name)
        if Template is None:
            pudge.log.debug('loading template: %s', name)
            Template = kid.load_template(name).Template
            self._template_cache[name] = Template
        import xml.parsers.expat
        try:
            return Template(generator=self,
                            browser=self.browser)
        except xml.parsers.expat.ExpatError, e:
            raise '%s: File "%s", line %d\n\t%r' \
                % (e, e.filename, e.lineno, e.source)
        
    def expand_template(self, name, destfile, output=None,
                        extension=None, **kw):
        t = self.get_template(name)
        for k, v in kw.items():
            setattr(t, k, v)
        t.settings = self.settings
        if t.settings:
            t.__dict__.update(self.settings)  # map settings to template attributes       
        basedir = self._ensure_dir(path.dirname(destfile))
        if extension is None:
            extension = self.file_extension
        t.destfile = destfile + extension #currently processed destination file
        filename = path.join(basedir,
                             os.path.basename(destfile) + extension)
        if output is None:
            if self.xhtml:
                output = 'xhtml-strict'
            else:
                output = 'html-strict'
        t.write(filename,
                fragment=self.fragment,
                output=output,
                encoding='utf-8')
                
    def load_documents(self):
        docs = []
        self.index_document = { 'title' : self.title, 'fragment' : '',
                                'basename': '' }
        document_files = [(path.splitext(path.basename(f))[0], f)
                           for f in self.document_files]
        if self.license:
            license_file = 'licenses/%s.rst' % (self.license, )
            document_files.append(('doc-license',
                                   resource_filename(__name__,
                                                     license_file)))
        for name, file in document_files:
            pudge.log.debug("loading rst document: %s" % (file,))
            parts = rst.parts(file)
            parts['basename'] = name
            parts['relative_filename'] = self._document_basename(file)
            relative_depth = len(parts['relative_filename'].split(os.path.sep))-1
            if relative_depth:
                parts['docroot'] = '/'.join(['..']*relative_depth) + '/'
            else:
                parts['docroot'] = ''
            if parts['relative_filename'] == 'index':
                self.index_document = parts
            else:
                docs.append(parts)
        self.documents = docs

    def _document_basename(self, filename):
        if self.doc_base:
            if not filename.startswith(self.doc_base):
                pudge.log.info("Document %s isn't under doc_base %s"
                               % (filename, self.doc_base))
            else:
                relative_filename = filename[len(self.doc_base):].lstrip(os.path.sep).lstrip('/')
                return os.path.splitext(relative_filename)[0]
        return os.path.splitext(os.path.basename(filename))[0]
        
    def get_document(self, name):
        for doc in self.documents:
            if doc['basename'] == name:
                return doc
    
    def generate_documents(self):
        for doc in self.documents:
            self.expand_template('document.html',
                                 doc['relative_filename'],
                                 parts=doc)
    
    def generate_index(self):
        self.expand_template('master-index.html', 'index')
        self.expand_template('package-index.html', 'module-index')
        
    def generate_modules(self):
        for m in self.browser.modules():
            if not m.obj: continue
            self.generate_module(m)

    def generate_module(self, m):
        self.time_func('  generate %s' % m.qualified_name(), self.generate_docstrings, m)
        for submodule in m.modules():
            self.generate_module(submodule)

    def generate_docstrings(self, m):
        self.check_module(m)
        filename = 'module-' + m.qualified_name()
        src_file = inspect.getsourcefile(m.obj)
        if self.needs_regeneration(filename, src_file):
            self.expand_template('module.html', filename,
                                 subject=m)
        filename += '-index'
        if self.needs_regeneration(filename, src_file):
            try:
                self.expand_template('module-index.html', filename,
                                     subject=m)
            except Exception, e:
                e.args = ('Error when rendering %s: %s' % (m.qualified_name(), e)),
                if 'rendering' not in str(e):
                    # Some exceptions don't print out their .args
                    print e.args[0]
                raise
        self.generate_classes(m)
        for submodule in m.modules():
            self.generate_module(submodule)
    
    def generate_classes(self, m):
        src_file = inspect.getsourcefile(m.obj)
        for c in m.classes():
            filename = 'class-' + c.qualified_name()
            if self.needs_regeneration(filename, src_file):
                self.expand_template('class.html', filename,
                                     subject=c)
    
    def check_module(self, m):
        #for msg in m.check_all_attribute():
        #    self.log(2, 'warn: %s' % msg)
        pass
    
    def needs_regeneration(self, dest_file, src_file, name=None):
        if self.force:
            return True
        if not os.path.exists(dest_file):
            return True
        if path.getmtime(dest_file) >= path.getmtime(src_file):
            pudge.log.debug('skipping: %s (fresh)' %
                            (name or dest_file))
            return False
        return True

    def generate_source(self):
        for m in self.browser.modules(recursive=1):
            module = m.obj
            if not module:
                pudge.log.debug('skipping: %s (no source file)'
                                % m.qualified_name())
                continue
            src_file = inspect.getsourcefile(module)
            if src_file is None:
                pudge.log.debug('skipping: %s (no source file)'
                                % m.qualified_name())
                continue
            src_stat = os.stat(src_file)
            dest_file = m.relative_file('.py%s' % self.file_extension)
            dest_file = path.join(self.dest, dest_file)
            if not self.needs_regeneration(dest_file, src_file,
                                           name=m.qualified_name()):
                continue
            pudge.log.info("colorizing: %s", dest_file)
            if not path.exists(path.dirname(dest_file)):
                os.makedirs(path.dirname(dest_file))
            fout = open(dest_file, 'w')
            colorizer.Parser(src_file, fout).format()
            fout.close()
            # Allow for atime resolution on windows and linux
            os.utime(dest_file, (src_stat[stat.ST_ATIME], src_stat[stat.ST_MTIME]))
        
    def copy_files(self):
        from shutil import copy
        from os import listdir
        from os.path import join, splitext, getmtime, exists
        extensions = ['.css', '.png', '.txt']
        templates = self.templates[:]
        templates.reverse()
        files = {}
        template_files = {}
        self._ensure_dir()
        for basedir in templates:
            for f in listdir(basedir):
                root, ext = splitext(f)
                if ext in extensions and not root.startswith('.'):
                    files[f] = join(basedir, f)
                if ext == '.kid':
                    template_files[f] = join(basedir, f)
        dest, force = self.dest, self.force
        for basename, file in files.items():
            destfile = join(dest, basename)
            if not force and exists(destfile):
                if getmtime(destfile) >= getmtime(file):
                    pudge.log.debug('skipping: %s (fresh)', file)
                    continue
            pudge.log.info('copying: %s -> %s', file, destfile)
            copy(file, self.dest)
        for basename, file in template_files.items():
            # expand_template adds dest, we don't have to:
            destfile = basename
            assert destfile.endswith('.kid')
            destfile = destfile[:-4]
            if not force and exists(destfile):
                # XXX: Should this test if variables have been modified?
                if getmtime(destfile) >= getmtime(file):
                    pudge.log.debug('skipping: %s (fresh)', file)
                    continue
            pudge.log.debug('rendering: %s -> %s', file, destfile)
            self.expand_template(basename, destfile, output='plain',
                                 extension='')
        
    def _ensure_dir(self, *dirs):
        p = path.join(self.dest, *dirs)
        if not path.exists(p):
            os.makedirs(p)
        return p

    def browser(self):
        if not hasattr(self, '_browser'):
            self._browser = browser.Browser(
                self.modules,
                self.exclude_modules)
        return self._browser
    browser = property(browser)

    def time_func(self, description, func, *args, **kw):
        """
        Time the function and record that (if self.profile is true).  Use the
        function name as the description is description is None.
        """
        if not self.profile:
            return func(*args, **kw)
        start = time.time()
        v = func(*args, **kw)
        end = time.time()
        if description is None:
            if hasattr(func, 'im_func'):
                func = func.im_func
            description = func.func_name
        if end-start > 0.1:
            self.profile_info.append(
                '%s: %s%4.1f secs' % (description, ' '*(45-len(description)),
                                     end-start))
        return v
    
    __call__ = generate

class Page(object):
    
    def link_to(self, obj):
        if not obj:
            return
        if obj.ismodule():
            path = 'module-%s.html' % (obj.qualified_name(), )
        elif obj.isclass():
            path = 'class-%s.html' % (obj.qualified_name(), )
        elif obj.isroutine() or obj.isdata():
            if obj.parent.ismodule():
                path = 'module-%s.html#%s'
            elif obj.parent.isclass():
                path = 'class-%s.html#%s'
            path = path % (obj.parent.qualified_name(),
                           obj.name)
        return path
    
    def link_to_source(self, obj):
        (line, last_line) = obj.source_lines()
        if line:
            hash = '#%d' % line
            params = '?f=%d&l=%d' % (line, last_line)
        else:
            line = '???'
            hash = params = ''
        return '%s.html%s%s' % (obj.relative_file(),
                                params, hash)
    
__all__ = ['Generator']
    
# module attributes    
__author__ = "Ryan Tomayko <rtomayko@gmail.com>"
__date__ = "$Date: 2007-01-07 19:08:36 -0800 (Sun, 07 Jan 2007) $"
__revision__ = "$Revision: 134 $"
__url__ = "$URL: svn://lesscode.org/pudge/trunk/pudge/generator.py $"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
