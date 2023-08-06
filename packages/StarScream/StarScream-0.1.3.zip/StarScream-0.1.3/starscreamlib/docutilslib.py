# docutils.py
# Copyright (C) 2008 Feihong Hsu http://feihonghsu.com
#
# This module is part of StarScream and is released under
# the New BSD License: http://www.opensource.org/licenses/bsd-license.php

import codecs
import docutils.core as dc
from pygments.formatters import HtmlFormatter
from docutils import nodes
from docutils.parsers.rst import directives
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer

def publish_parts(filename):
    """Invoke docutils's publish_parts function on the content contained within
    ``filename``.  The returned dictionary also contains the keys and values
    obtained from the InfoDirective instance."""
    infodir = InfoDirective()
    cssfiledir = FileDirective()

    directives.register_directive('info', infodir)
    directives.register_directive('cssfile', cssfiledir)
    
    parts = dc.publish_parts(source=codecs.open(filename, 'r', 'utf-8').read(),
                             writer_name='html')

    parts.update(infodir.info)
    parts['cssfiles'] = cssfiledir.files
        
    return parts

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    """This is a reST directive for producing syntax highlighted HTML."""
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        lexer = TextLexer()
        
    formatter = HtmlFormatter()

    if 'file' in options:
        text = open(options['file']).read()
    else:
        text = u'\n'.join(content)

    parsed = highlight(text, lexer, formatter)
    return [nodes.raw('', parsed, format='html')]

pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
pygments_directive.options = {'file': directives.unchanged}

directives.register_directive('code', pygments_directive)

class InfoDirective(object):
    """Instances of InfoDirective implement reST directives that are able to
    parse simple text blocks of the following form:

        author = Feihong Hsu
        venue = PyCon 2008
        location = Chicago, USA
        date = March 14, 2007

    The keys and values in the above text block are stored in a dictionary
    attribute called ``info``.
    """
    def __init__(self):
        self.info = {}
        self.content = 1
        
    def __call__(self, name, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
        for line in content:
            line = line.strip()
            if line:
                k, v = line.split('=', 1)
                k = str(k).strip()
                self.info[k] = v.strip()
        
        return []

class FileDirective(object):
    def __init__(self):
        self.files = []
        self.arguments = (1, 0, 1)
        
    def __call__(self, name, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
        self.files.extend(arguments)
        return []
        
if __name__ == '__main__':
    parts = publish_parts('slides.txt')
##    open('handout.html', 'w').write(
##        template.substitute(title=parts['title'], content=parts['body'])
##    )

    print '\nDone!\n'
