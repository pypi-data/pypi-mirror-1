#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  scrape_higlighted.py
#  scrape-highlighted
# 
#  Created by Lars Yencken on 04-05-2009.
#  Copyright 2009 NICTA. All rights reserved.
#

"""
Scrapes highlighted text from pdf files.
"""

import os, sys, optparse

from appscript import *

skim = None

def fetch_annotations(filename, prefix=False):
    global skim
    if skim is None:
        skim = app('Skim')

    if not os.path.exists(filename):
        print >> sys.stderr, "No such file: %s" % filename
    abs_filename = os.path.abspath(filename)
    skim.open(abs_filename)
    document = skim.documents[1] # applescript is 1-indexed
    document.convert_notes()
    for i, page in enumerate(document.pages.get()):
        for note in page.notes.get():
            if note.type.get() == k.highlight_note:
                selection = note.selection()
                if not selection:
                    continue

                text = page.get_text_for(selection).get()
                if '\n' in text:
                    text.replace('\n', '\\n')
                
                if prefix:
                    print '%s: %s' % (filename, text)
                else:
                    print text
    document.revert()
    document.close()

#----------------------------------------------------------------------------#

def _create_option_parser():
    usage = \
"""%prog [options] file1.pdf [file2.pdf [...]]

Extracts all highlighted text from the given pdf file."""

    parser = optparse.OptionParser(usage)

    return parser

def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if not args:
        parser.print_help()
        sys.exit(1)

    for filename in args:
        fetch_annotations(filename, prefix=(len(args) > 1))

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    main(sys.argv[1:])

# vim: ts=4 sw=4 sts=4 et tw=78:
