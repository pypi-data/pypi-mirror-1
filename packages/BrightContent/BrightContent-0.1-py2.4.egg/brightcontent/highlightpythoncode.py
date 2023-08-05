# Copied from: http://www.lethalman.net/2006/03/11/markdown-extension-to-highlight-python-code/
# Requires py2html: http://www.peck.org.uk/p/python/

import py2html
import os
import tempfile

class HighlighterExtension:
    style = py2html.py_style
    for key, value in style.iteritems():
        value[0] += ' '
   
    def __init__ (self):
        self.CODE_RE = '\[\[\[(.*?)\]\]\]'

    def extendMarkdown(self, md):
        self.md = md
        escape_idx = md.inlinePatterns.index(ESCAPE_PATTERN)+1
        md.inlinePatterns.insert(escape_idx, HighlighterPattern(self.CODE_RE, self))

class HighlighterPattern(BasePattern):
    def __init__(self, pattern, ext):
        BasePattern.__init__(self, pattern)
        self.ext = ext
       
    def handleMatch(self, m, doc):
        code = m.group(2).strip()
        fd, fname = tempfile.mkstemp()
        f = file(fname, 'w')
        f.write(code)
        f.close()
        result = py2html.file2HTML(fname, 0, self.ext.style, True)
        os.unlink(fname)
        place_holder = self.ext.md.htmlStash.store(result)
        return doc.createTextNode(place_holder)
 

