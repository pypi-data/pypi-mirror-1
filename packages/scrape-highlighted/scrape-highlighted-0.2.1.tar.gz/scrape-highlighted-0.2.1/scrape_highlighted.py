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
import re
import string

from consoleLog import withProgress
from appscript import app, k, CommandError

skim = None

def fetch_annotations(filename, prefix='', ostream=sys.stdout, 
        debug=False):
    """
    Fetches annotations from the pdf file by running it through Skim and
    using the applescript bridge to scrape highlighted text.
    """
    global skim
    if skim is None:
        skim = app('Skim')

    if not os.path.exists(filename):
        if debug:
            raise Exception('no such file %s' % filename)

        _log_file_missing(ostream, prefix)
        return

    notes, errors = _scrape_document(filename)
    _log_notes(notes, ostream, prefix)
    if errors and debug:
        raise errors[0]

    for e in errors:
        if isinstance(e, CommandError):
            _log_error(ostream, prefix, 'COMMAND ERROR')
        elif isinstance(e, UnicodeDecodeError):
            _log_error(ostream, prefix, 'UNICODE ERROR')
        else:
            raise e

def _scrape_document(filename):
    """
    Returns a list of all highlighted text in the document.
    """
    global skim
    abs_filename = os.path.abspath(filename)
    skim.open(abs_filename)
    document = skim.documents[1] # applescript is 1-indexed
    document.convert_notes()

    notes = []
    errors = []
    for i, page in enumerate(document.pages.get()):
        for note in page.notes.get():
            if note.type.get() == k.highlight_note:
                parts = []
                for part in note.selection.get():
                    try:
                        parts.append(part.get())
                        continue
                    except CommandError:
                        pass
                        
                    part_range = re.findall(r"'cha '\).byindex\(([0-9]+)\)", 
                            str(part.AS_aemreference))
                    start, stop = map(int, part_range)

                    try:
                        value = ''.join(
                                page.text.characters[start:stop].get()
                            )
                        parts.append(value)
                    except UnicodeDecodeError, e:
                        errors.append(e)
                
                notes.append('\t'.join(parts))

    document.revert()
    document.close()
    
    notes = filter(None, map(string.strip, notes))
    return notes, errors

def _log_notes(notes, ostream, prefix):
    if not notes:
        print >> ostream, '%s%s' % (prefix, 'NONE')
        ostream.flush()
        return
    
    for note in notes:
        note = note.replace('\n', '\\n')
        print >> ostream, '%s%s' % (prefix, note)
        ostream.flush()
    
    return

def _log_error(ostream, prefix, error):
    print >> ostream, '%s%s' % (prefix, error)
    ostream.flush()
    
def _log_file_missing(ostream, prefix):
    print >> ostream, '%sNO SUCH FILE' % prefix
    ostream.flush()
    
#----------------------------------------------------------------------------#

def _create_option_parser():
    usage = \
"""%prog [-o output] file1.pdf [file2.pdf [...]]

Extracts all highlighted text from the given pdf file."""

    parser = optparse.OptionParser(usage)

    parser.add_option('-o', '--output', action='store', dest='output_file',
            help='Store the output to the given file instead of stdout')
    
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
            help='Run in debug mode, stopping on failures [False]')

    return parser

def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if not args:
        parser.print_help()
        sys.exit(1)

    if options.output_file:
        ostream = open(options.output_file, 'w')
    else:
        ostream = sys.stdout

    if len(args) == 1:
        fetch_annotations(args[0], ostream=ostream, debug=options.debug)

    else:
        filenames = args
        if options.output_file:
            filenames = withProgress(filenames)
        
        for filename in filenames:
            fetch_annotations(filename, prefix='%s: ' % filename,
                    ostream=ostream, debug=options.debug)

    if options.output_file:
        ostream.close()

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    main(sys.argv[1:])

# vim: ts=4 sw=4 sts=4 et tw=78:
