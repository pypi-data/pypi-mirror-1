"""Pudge package.

The `pudge.generator.Generator` class can be used to generate Python
documentation::

    from pudge.generator import Generator
    generator = Generator()
    generator.title = 'Foo Documentation'
    generator.license = 'gnu'
    generator.dest_dir = '/tmp/documentation'
    generator.modules = ['foo']
    generator()
    
This package contains modules for generating documentation from Python
source code. The `pudge.generator.Generator` class uses the `peruser`
and `scanner` modules to inspect a package/module hierarchy, the
`colorizer` and `rst` modules to generate HTML files and fragments.

"""

import logging

# the logger object used by all modules.
log = logging.getLogger('pudge')

__all__ = ['generator', 'scanner', 'colorizer', 'cli', 'rst',
           'log', 'browser']


# module attributes
__author__ = "Ryan Tomayko <rtomayko@gmail.com>"
__date__ = "$Date: 2006-03-11 13:03:49 -0800 (Sat, 11 Mar 2006) $"
__revision__ = "$Revision: 122 $"
__url__ = "$URL: svn://lesscode.org/pudge/trunk/pudge/__init__.py $"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__version__ = "0.1.2"
