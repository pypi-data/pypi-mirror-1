# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

import os
import os.path

try:
    import buildutils
except ImportError:
    pass

import pudge as package

name = package.__name__
version = package.__version__
doc_parts = package.__doc__.strip().splitlines()

def get_data_files(relpath, files=None):
    global name, os, get_data_files
    BASEDIR = name
    if files is None:
        files = []
    for file in os.listdir(os.path.join(BASEDIR, relpath)):
        if file.startswith("."):
            continue
        fn = os.path.join(relpath, file)
        if os.path.isdir(os.path.join(BASEDIR, fn)):
            get_data_files(fn, files)
        elif os.path.isfile(os.path.join(BASEDIR, fn)):
            if fn.endswith('.pyc'):
                continue
            files.append(fn)
    return files

package_data = []
for subdir in [('template', ),
               ('licenses', )]:
    package_data.extend(get_data_files(os.path.join(*subdir)))

from setuptools import setup

setup(
    name=name,
    version=version,
    description="Pudge is a documentation generator for Python projects, using Restructured Text",
    author="Ryan Tomayko",
    author_email="rtomayko@gmail.com",
    license="MIT",
    long_description="""\
Pudge renders `reStructured Text
<http://docutils.sourceforge.net/rst.html>`_ documentation, extracts
documentation from docstrings, and colorizes source to create project
websites.

Pudge is only available by checkout from the `Subversion respository
<svn://lesscode.org/pudge/trunk#egg=Pudge-dev>`_ at
http://lesscode.org/svn/pudge/ or ``easy_install Pudge==dev``
    """,
    keywords = "documentation doc html",
    platforms = ["any"],
    url = "http://lesscode.org/projects/%s/" % name,
    #download_url = "http://lesscode.org/dist/%s/%s-%s.tar.gz" % \
    #               (name, name, version),
    py_modules = [],
    packages = [name, name + '.test'],
    scripts = ['bin/%s' % name],
    install_requires=['kid>=0.7.1', 'docutils'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    package_data = { name : package_data }
)

