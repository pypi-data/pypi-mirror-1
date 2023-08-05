#!/usr/bin/env python2.3
""" Build the contents of doc/ directory from sources """
import time,os

import empywiz as prjwiz
import expandtemplate

open("doc/prjwiz.txt","w").write(prjwiz.__doc__)
open("doc/expandtemplate.txt","w").write(expandtemplate.__doc__)
versionfile ="""\
pywiz %s
Build: %s
License: %s
""" % (expandtemplate.__version__,
       time.asctime(),
       expandtemplate.__license__
       )

os.chdir("doc")

# You need python 'docutils' to produce pretty html versions of the
# reStructuredText-formatted docs. adjust the path accordingly.

os.system(r"~/docutils-0.3/tools/buildhtml.py")
os.chdir("..")


open("doc/version.txt","w").write(versionfile)
