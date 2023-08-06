#!/usr/bin/python
#$Id: export.py 5290 2004-05-27 20:42:09Z longsleep $
#Copyright: ClearWind Consulting Ltd
#License: http://www.clearwind.ca/license

# Use this script for building a clean Plone tarball
# for the website
#
# You need to pass: CVS tag and Username
# 
# I'll assume you've got SSH keys set up for Plone

import os
import sys

if len(sys.argv) < 3:
    print "Usage: script username cvstag"
    sys.exit(1)

cvs = 'cvs -d:ext:%s@cvs.sf.net:/cvsroot/plone export -r %s CMFPlone'
cvs = cvs % (sys.argv[1], sys.argv[2])
os.system(cvs)

assert os.path.exists('CMFPlone'), "Check out failed?"

version = open('CMFPlone/version.txt').read().strip()

tar = 'tar cf CMFPlone-%s.tar CMFPlone' % version
os.system(tar)

gzip = 'gzip CMFPlone-%s.tar' % version
os.system(gzip)
os.system('rm -rf CMFPlone')
