"""Command line interface."""

usage = """
Generate documentation for Python projects.

OPTIONS:

  -d, --dest=DIR     Directory where documentation should be generated.
  -i, --documents=FILE...
                     Comma seperated list of files
  -c, --title=TEXT   The title of the documentation set. This is used in
                     various places in generated documentation and defaults
                     to "Module Reference". If you include a document named
                     "index", the title from that document is used.
  -f, --force        Force creation of documentation files even if source
                     files are older or the same age.
      --license=NAME Include a standard license document. Current options
                     are "gnu" for the GNU Free Documentation License and
                     "cc" for a Creative Commons Attribution, NonCommercial,
                     Copyleft license.
  -x, --xhtml        Generate XHTML 1.0 instead of HTML 4.01.
                     HTML 4.01 is the default due to browser compatibility
                     issues with XHTML 1.0.
  -e, --ext=TEXT     The file extension to use when writing (X)HTML files.
                     The default is '.html'
      --stages=LIST  Specify the list of stages that should be performed.
                     This allows only portions of the generation to take
                     place. Available stages are: copy, docs, reference,
                     index, and source.
  -t, --templates=.. The directory where we should look for templates. See
                     the 'pudge.templates' package directory for the default
                     template set.
      --theme=NAME   The name of a built-in theme (overrides --templates).
      --trac=URL     Adds navigational links to a Trac site.
      
  -v, --verbose      Verbose output.
  -q, --quiet        Shutup unless something important happens.
  -h, --help         print this help screen.

Examples:

Generate documentation for 'foo' to current directory:

  $ pudge -m foo

Generate documentation for 'foo' module/package and two documents to 'build/doc':

  $ pudge --modules=foo --documents=docs/guide.rst,docs/reference.rst \
          --dest=build/doc

Generate documentation for the 'foo' module/package and license the work
under the GNU Free Documentation License:

  $ pudge --license=gnu --modules=foo

Pudge is Copyright (c) 2005 by Ryan Tomayko <http://naeblis.cx/rtomayko/>
"""

import sys
import getopt
import logging

import pudge
import pudge.generator

def main():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    pudge.log.addHandler(handler)
    pudge.log.setLevel(logging.INFO)
    command = PudgeCommand()
    command.process_command()

class PudgeCommand:
    """Handles command line invocation."""
    
    def __init__(self, command=None, args=[]):
        self.command = command or sys.argv[0]
        self.args = args or sys.argv[1:]
        
    def usage(self, msg=None, exit_with=None):
        if msg:
            print msg
            print "  try: %s --help" % (self.command, )
        else:
            print 'usage: %s [OPTIONS]' % (self.command, )
            print usage.strip()
        if exit_with is not None:
            sys.exit(exit_with)
        
    def parse_arguments(self):
        opts, args = getopt.getopt(self.args, 'hfxqve:d:i:l:m:t:',
                                   ['help', 'force', 'xhtml', 'quiet',
                                    'verbose',
                                    'ext=', 'dest=', 'documents=',
                                    'license=', 'trac=',
                                    'title=', 'theme=', 'modules=', 
                                    'templates='])
        # TODO handle ImportError, AttributeError, SyntaxError etc...
        generator = pudge.generator.Generator()
        for o, a in opts:
            if o in ('-h', '--help'):
                return self.usage
            elif o in ('-d', '--dest'):
                generator.dest = a
            elif o in ('-e', '--ext'):
                generator.file_extension = a
            elif o in ('-f', '--force'):
                generator.force = 1
            elif o in ('-q', '--quiet'):
                pudge.log.setLevel(logging.WARN)
            elif o in ('-v', '--verbose'):
                pudge.log.setLevel(logging.DEBUG)
            elif o in ('-l', '--title'):
                generator.title = a
            elif o == '--license':
                assert a in ('gnu', 'cc'), "--license should be 'gnu' or 'cc'"
                generator.license = a
            elif o in ('-m', '--modules'):
                generator.modules = a.split(',')
            elif o in ('-i', '--documents'):
                generator.document_files = a.split(',')
            elif o in ('-t', '--templates'):
                generator.template_dir = a
            elif o in ('--theme', ):
                generator.theme = a
            elif o in ('-x', '--xhtml'):
                generator.xhtml = 1
            elif o == '--trac':
                generator.trac_url = a
        if not generator.modules and not generator.document_files:
            self.usage('Must specify --modules or --documents.', exit_with=99)
            return
        return generator
    
    def process_command(self):
        try:
            command = self.parse_arguments()
        except Exception, e:
            raise
            self.usage(str(e), exit_with=2)
        else:
            command()

__all__ = ['PudgeCommand']

# module attributes
__author__ = "Ryan Tomayko <rtomayko@gmail.com>"
__date__ = "$Date: 2005-07-01 05:09:30 -0700 (Fri, 01 Jul 2005) $"
__revision__ = "$Revision: 54 $"
__url__ = "$URL: svn://lesscode.org/pudge/trunk/pudge/cli.py $"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

if __name__ == '__main__':
    main()
