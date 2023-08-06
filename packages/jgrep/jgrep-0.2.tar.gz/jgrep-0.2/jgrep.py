#!/usr/bin/env python
from __future__ import with_statement

import sys
from optparse import OptionParser

from json_grep import JSONGrep

# -----------------------------------
# Main
# -----------------------------------
def parse_args():
    parser = OptionParser()
    parser.add_option('-k', '--key' , dest='keys', action='append',
                     help='List of JSON keys to output, arg for each key')
                     
    options, args = parser.parse_args()

    if not options.keys:
        parser.error('Must specify at least one key regex')
        sys.exit()

    return options, args

if __name__ == '__main__':
    options, args = parse_args()
    json_grep = JSONGrep(options.keys)
   
    if len(args) == 1:   
        with open(args[0]) as fd:    
            for line in json_grep.jgrep_file(fd):
                print '%s' % line
    else:
        for line in json_grep.jgrep_file(sys.stdin):
            print '%s' % line           
