# starscream.py
# Copyright (C) 2008 Feihong Hsu http://feihonghsu.com
#
# This script is part of StarScream and is released under
# the New BSD License: http://www.opensource.org/licenses/bsd-license.php

import sys, os
from starscreamlib import *

usageText = """\
Usage: starscream.py action
actions:
    all
      Generate files for both slides and handout

    slides
      Generate the files slides.html and slides.js

    handout
      Generate the handout.html file

    project
      Create the directory structure and initial files for a new
      presentation project"""    

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print usageText
        sys.exit(0)

    action = sys.argv[1]

    if action == 'slides':
        build_slides('slides.txt')
    elif action == 'handout':
        build_handout('slides.txt')
    elif action == 'project':
        cwd = os.getcwd()
        copy_css_files(cwd)
        copy_script_files(cwd)
        copy_file('slides.txt', cwd)
    elif action == 'all':
        build_slides('slides.txt')
        build_handout('slides.txt')
    else:
        print usageText
