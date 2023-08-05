"""Python source code colorizer.

This module is derived from MoinMoin's [1] python source parser, described
in the following recipe:

<http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52298>

.. [1] http://moin.sourceforge.net/

"""

# Imports
import cgi, string, sys, cStringIO
import keyword, token, tokenize
import re

#############################################################################
### Python Source Parser (does Hilighting)
#############################################################################

_KEYWORD = token.NT_OFFSET + 1
_TEXT    = token.NT_OFFSET + 2

_styles = {
    token.NUMBER:       'number',
    token.OP:           'op',
    token.STRING:       'string',
    tokenize.COMMENT:   'comment',
    token.NAME:         'name',
    token.ERRORTOKEN:   'error',
    _KEYWORD:           'keyword',
    _TEXT:              'text',
}

class Parser:
    """ Send colored python source."""

    def __init__(self, filename, out = sys.stdout):
        """ Store the source text.
        """
        self.filename = filename
        self.raw = open(filename, 'r').read().expandtabs().strip()
        self.out = out
        
    def format(self):
        """ Parse and send the colored source."""
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find('\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))
        
        # parse the source and write it
        self.out.write('''<html><head><title>%s</title>
        <script type="text/javascript"><!--
        %s
        // --></script>
        <style>
        div.python {
          color: #333
        }
        div.python a.lnum {
          color: #555;
          background-color: #eee;
          border-right: 1px solid #999;
          padding-right: 2px;
          margin-right: 4px;
        }
        div.python span.comment { color: #933 }
        div.python span.keyword { color: #a3e; font-weight: bold  }
        div.python span.op { color: #c96 }
        div.python span.string { color: #6a6 }
        div.python span.name { }
        div.python span.text { color: #333 }
        div.highlighted { background-color: #ff9; border: 1px solid #009 }
        </style></head><body onload="show_line_range()">''' % (
            cgi.escape(self.filename), highlight_javascript))
        self.out.write('<div class="python"><code>')
        self.write_line(1, br='')
        self.pos = 0
        text = cStringIO.StringIO(self.raw)
        self.run_tokens(tokenize.generate_tokens(text.readline))
        self.out.write('</code></div>')
        self.out.write('</body></html>')
        self.out.flush()
        self.out.close()
        
    def write_line(self, line_num, br='<br />\n'):
        fmt = str(line_num).rjust(4,'0')
        self.out.write(
                '%s<a class="lnum" href="#%d" name="%d">%s</a>' \
                % (br, line_num, line_num, fmt))
        
    def run_tokens(self, it):
        """ Token handler."""
        for tok in it:
            (toktype, toktext, (srow,scol), (erow,ecol), line) = tok
            if 0:
                print repr((toktype, token.tok_name[toktype], toktext,
                            srow,scol, erow,ecol))
        
            # calculate new positions
            oldpos = self.pos
            newpos = self.lines[srow] + scol
            self.pos = newpos + len(toktext)

            # handle newlines
            if toktype in [token.NEWLINE, tokenize.NL]:
                self.write_line(srow+1)
                continue
            
            # send the original whitespace, if needed
            if newpos > oldpos:
                ws = self.raw[oldpos:newpos]
                self.out.write('&#0160;' * len(ws))
                
            # skip indenting tokens
            if toktype in [token.INDENT, token.DEDENT]:
                self.pos = newpos
                continue
            
            # map token type to a color group
            if token.LPAR <= toktype and toktype <= token.OP:
                toktype = token.OP
            elif toktype == token.NAME and keyword.iskeyword(toktext):
                toktype = _KEYWORD
            style = _styles.get(toktype, _styles[_TEXT])
            
            # send text
            self.runlines(toktext, srow, '<span class="%s">%%s</span>' % style)


    def runlines(self, text, line_num, interpolate):
        if '\n' in text:
            lines = text.split('\n')
            for i, line in zip(range(len(lines)), lines):
                if i > 0: self.write_line(line_num + i)
                self.out.write(interpolate % cgi.escape(line).replace(' ', '&#0160;'))
        elif text:
            self.out.write(interpolate % cgi.escape(text).replace(' ', '&#0160;'))

highlight_javascript = """
function show_line_range() {
    var href = document.location.href;
    if (href.indexOf('?') == -1) {
        return;
    }
    var qs = href.substring(href.indexOf('?')+1);
    if (qs.indexOf('#') >= 0) {
        qs = qs.substring(0, qs.indexOf('#'));
    }
    var first = qs.match(/f=(\d+)/)[1];
    var last = qs.match(/l=(\d+)/)[1];
    if (! first || ! last) {
        return;
    }
    var anchors = document.getElementsByTagName('A');
    var container = document.createElement('DIV');
    container.className = 'highlighted';
    var children = [];
    var start = null;
    var parent = null;
    var highlight = false;
    for (var i = 0; i < anchors.length; i++) {
        var el = anchors[i];
        if (el.getAttribute('name') == first) {
            start = el.previousSibling;
            parent = el.parentNode;
            highlight = true;
        }
        if (el.getAttribute('name') == last) {
            break;
        }
        if (highlight) {
            children[children.length] = el;
            el = el.nextSibling;
            while (el && el.tagName != 'A') {
                children[children.length] = el;
                el = el.nextSibling;
            }
        }
    }
    for (i=0; i<children.length; i++) {
        container.appendChild(children[i]);
    }
    if (start) {
        start.parentNode.insertBefore(container, start.nextSibling);
    } else {
        parent.insertBefore(container, parent.childNodes[0]);
    }
}
"""

__all__ = ['Parser']

# module attributes
__author__ = "Ryan Tomayko <rtomayko@gmail.com>"
__date__ = "$Date: 2006-01-08 15:28:12 -0800 (Sun, 08 Jan 2006) $"
__revision__ = "$Revision: 107 $"
__url__ = "$URL: svn://lesscode.org/pudge/trunk/pudge/colorizer.py $"
__copyright__ = "Copyright 2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
