#!/usr/bin/env python
"""
Takes the runpon-cfg.glade and bz2-zip it and encode it to base64;
the output can be pasted in the runpon.py script.
"""

fd = open('runpon-cfg.glade', 'r')
fc = fd.read()
fd.close()

print 'CFG_GTKBUILDER =', repr(fc.encode('bz2').encode('base64'))

