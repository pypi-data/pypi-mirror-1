# common.py
# Copyright (C) 2008 Feihong Hsu http://feihonghsu.com
#
# This module is part of StarScream and is released under
# the New BSD License: http://www.opensource.org/licenses/bsd-license.php

import re

def remove_timestamps(tree):
    """Remove timestamps of the form <1:30> from the section titles"""
    pattern = re.compile(r"\<\d+\:\d+\>")

    def get_new_title(text):
        m = pattern.search(text)
        return text[:m.start()].strip() if m else text

    for h1 in tree.xpath('div/h1'):
        a = h1.xpath('a')
        if a:
            title = get_new_title(a[0].text)
            h1.remove(a[0])
            h1.text = title

def get_css_links(cssfiles):
    """``cssfiles`` is a list of CSS file names. Return a chunk of HTML
    markup that links to each CSS file."""
    return '\n'.join(
        '<link rel="stylesheet" type="text/css" href="%s" />' % f
        for f in cssfiles)

def get_javascript_links(jsfiles):
    """``jsfiles`` is a list of JavaScript file names. Return a chunk of HTML
    markup that links to each JavaScript file."""
    return '\n'.join(
        '<script type="text/javascript" src="%s"></script>' % f
        for f in jsfiles)


