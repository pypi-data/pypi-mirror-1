#!/usr/bin/env python

""" Install common Gazest dependencies in a workingenv friendly way. """

import os
import sys

PYPI = "http://pypi.python.org/packages/source"

def fail(msg):
    print msg
    sys.exit(1)

cmd = "svn co http://authkit.org/svn/AuthKit/tags/0.4.0/ authkit-0.4.0"
if os.system(cmd):
    fail("can't fetch authkit")

os.chdir("authkit-0.4.0")
cmd = "%s setup.py install" % sys.executable
if os.system(cmd):
    fail("can't install authkit")
os.chdir("..")

cmd = "easy_install %s" % "http://effbot.org/downloads/Imaging-1.1.6.tar.gz"
if os.system(cmd):
    fail("can't install PIL")


# if 2.4, more deps
PY_MAJ = sys.version_info[:2]
if PY_MAJ < (2, 4):
    print "You need Python 2.4 or later"
    sys.exit(1)
elif PY_MAJ == (2, 4):
    cmd = "easy_install uuid hashlib"
    if os.system(cmd):
        fail("can't install 2.4 extra deps")

print "\n" + "-"*30
print "Done!"
print "You should be OK now but this have not been tested that much..."
