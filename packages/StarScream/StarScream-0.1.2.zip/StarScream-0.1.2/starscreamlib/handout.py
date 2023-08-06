# handout.py
# Copyright (C) 2008 Feihong Hsu http://feihonghsu.com
#
# This module is part of StarScream and is released under
# the New BSD License: http://www.opensource.org/licenses/bsd-license.php

import re, string, codecs
from lxml import etree
from docutilslib import publish_parts
import common

def build_handout(filename):
    """From the reST file ``filename``, generate the following
    ``handout.html`` file"""
    parts = publish_parts(filename)

    tree = etree.fromstring('<root>%s</root>' % parts['body'])
    common.remove_timestamps(tree)
    modify_notes_nodes(tree)

    parts['body'] = etree.tostring(tree)[6:-7]
    parts['csslinks'] = common.get_css_links(parts['cssfiles'])

    codecs.open('handout.html', 'w', 'utf-8').write(
        template.substitute(**parts)
    )

def modify_notes_nodes(tree):
    """Visit all non-top-level nodes, change their class attribute to 'notes'"""
    nodes = tree.xpath("div//div[@class='section']")
    for node in nodes:
        node.set('class', 'notes')
        node.remove(node[0])

# This is the template for the entire handout document
template = string.Template("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>${title}</title>
<link rel="stylesheet" type="text/css" href="handout.css" />
$csslinks
<body>
<div id="info">
    <div id="title">${title}</div>
    <div id="author">${author}</div>
    <div id="venue">${venue}</div>
    <div id="location">${location}</div>
    <div id="date">${date}</div>
</div>
${body}
</body>
</html>
""")

if __name__ == '__main__':
    build_handout('slides.txt')
    print '\nDone!\n'
