#!/usr/bin/env python

import sys
from os.path import split, basename

def find_path ():
    for path in sys.path:
	(head, tail) = split (path)
	if tail == 'site-packages':
	    base = basename (head)
	    print path
	    #print base + '/' + tail
	    return

find_path ()
