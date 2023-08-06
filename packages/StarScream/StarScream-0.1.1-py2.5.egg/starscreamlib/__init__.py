# __init__.py
# Copyright (C) 2008 Feihong Hsu http://feihonghsu.com
#
# This module is part of StarScream and is released under
# the New BSD License: http://www.opensource.org/licenses/bsd-license.php

import sys, os, os.path as op
from pkg_resources import resource_string
from handout import build_handout
from slides import build_slides

def copy_css_files(dest):
    """Copy all the CSS files into the specified directory"""
    for f in ['handout', 'slide', 'syntax']:
        cssfile = f + '.css'
        copy_file(cssfile, dest)

def copy_script_files(dest):
    """Copy all the JS files into a ``scripts`` directory inside the
    specified directory. Create the ``scripts`` directory if necessary."""
    scriptDir = op.join(dest, 'scripts')
    if not op.exists(scriptDir):
        os.mkdir(scriptDir)

    for f in ['jquery.dimensions', 'jquery.gradient', 'jquery', 'scripts']:
        jsfile = f + '.js'
        copy_file('scripts/' + jsfile, dest)

def copy_file(name, dest):
    """Write the contents of ``name`` (a file in this module) to the
    directory ``dest``"""
    print name
    destFile = op.join(dest, name)
    if op.exists(destFile):
        return
    
    fout = open(destFile, 'wb')
    fout.write(resource_string(__name__, name))
    fout.close()
