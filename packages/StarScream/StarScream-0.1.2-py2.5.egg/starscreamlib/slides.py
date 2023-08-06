# slides.py
# Copyright (C) 2008 Feihong Hsu http://feihonghsu.com
#
# This module is part of StarScream and is released under
# the New BSD License: http://www.opensource.org/licenses/bsd-license.php

import re, string, traceback, codecs
from lxml import etree
import simplejson
from docutilslib import publish_parts
from common import remove_timestamps, get_css_links

def build_slides(filename):
    """From the reST file ``filename``, generate the following files:

        - slides.html  <- a basic HTML page
        - slides.js    <- JS file containing the inner HTML for each slide
    """
    parts = publish_parts(filename)
    parts['csslinks'] = get_css_links(parts['cssfiles'])

    tree = etree.fromstring(parts['html_body'])

    try:
        remove_timestamps(tree)
        remove_notes(tree)
        create_slides(parts, tree)
    except:
        traceback.print_exc()
        print 'Please fix the errors in', filename
        open('slides.html', 'w').write(
            etree.tostring(tree)
        )

def remove_notes(tree):
    """Remove all div elements that are not at the top level. Also clear
    all attributes from top level div elements."""
    for node in tree.xpath('div'):
        node.attrib.clear()
        
        for node2 in node.xpath("div[@class='section']"):
            node.remove(node2)

def create_slides(parts, tree):
    """Generate the two files: ``slides.js`` and ``slides.html``"""
    # Generator function that returns a JavaScript string for each slide
    def get_slide_reprs():
        yield simplejson.dumps(titleTemplate.substitute(**parts))
        
        for node in tree.xpath("div"):
            h1 = node[0]
            node.remove(h1)
            node.set('id', 'content')

            html = '<h1 id="header">%s</h1>%s' % (h1.text, etree.tostring(node))
            yield simplejson.dumps(html)

    # Generate the slides.js file:
    fout = open('slides.js', 'w')
    fout.write('slides = [\n\t')

    for i, s in enumerate(get_slide_reprs()):
        if i != 0:
            fout.write(',\n\t')
        fout.write(s)
        
    fout.write('\n]')
    fout.close()

    # Generate the slides.html file:
    codecs.open('slides.html', 'w', 'utf-8').write(
        htmlTemplate.substitute(**parts)
    )

# This template is for generating the HTML for the title slide
titleTemplate = string.Template("""\
<div id="info">
    <div id="title">${title}</div>
    <div id="author">${author}</div>
    <div id="venue">${venue}</div>
    <div id="location">${location}</div>
    <div id="date">${date}</div>
</div>""")

# This template is for generating the slides.html file
htmlTemplate = string.Template("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>${title}</title>
<link rel="stylesheet" type="text/css" href="slide.css" />
$csslinks
<script type="text/javascript" src="slides.js"></script>
<script type="text/javascript" src="scripts/jquery.js"></script>
<script type="text/javascript" src="scripts/jquery.dimensions.js"></script>
<script type="text/javascript" src="scripts/jquery.gradient.js"></script>
<script type="text/javascript" src="scripts/scripts.js"></script>
<body>
    <div id="slide">
        <h1 id="header">Error!</h1>
        <div id="content">You need to turn on JavaScript to run the slideshow</div>
    </div>
</body>
</html>""")
        
if __name__ == '__main__':
    build_slides('slides.txt')
    print '\nDone!\n'
