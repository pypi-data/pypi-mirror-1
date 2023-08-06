#!/usr/bin/env python
"""
Takes the given *.glade, bz2-zip it and encode it to base64;
the output can be pasted in the runpon.py script.
"""

import sys

if len(sys.argv) != 2:
    print './runpon-cfg.glade FILE.glade'
    sys.exit(0)

fd = open(sys.argv[1], 'r')
fc = fd.read()
fd.close()

print 'GLADE_DEFINITION =', repr(fc.encode('bz2').encode('base64'))

