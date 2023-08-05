#!/usr/bin/env python

import os
import sys
import subprocess
import re

externals = {"cherrypy" : "http://svn.cherrypy.org/tags/cherrypy-2.2.1/",
"sqlobject" : "http://svn.colorstudy.com/SQLObject/branches/0.7/",
"mochikit" : "http://svn.mochikit.com/mochikit/tags/MochiKit-1.3.1/",
"kid" : "svn://svn.kid-templating.org/tags/0.9.3/",
"formencode" : "http://svn.colorstudy.com/FormEncode/tags/0.7.1/",
"paste" : "http://svn.pythonpaste.org/Paste/tags/0.5/",
"pastescript" : "http://svn.pythonpaste.org/Paste/Script/tags/1.0/",
}

urlline = re.compile("^URL: (.*)")

def update(proj):
    os.chdir(proj)
    svninfo = subprocess.Popen(["svn", "info"], stdout=subprocess.PIPE)
    out = svninfo.stdout
    line = out.readline()
    while line:
        line = out.readline()
        url = urlline.match(line)
        if url:
            url = url.group(1).strip()
            if url != externals[proj] and url != externals[proj][:-1]:
                print "Switching project %s to %s" % (proj, externals[proj])
                svnswitch = subprocess.call(["svn", "switch", externals[proj], "."])
            else:
                print "Updating project %s" % (proj)
                svnupdate = subprocess.call(["svn", "update"])
            break
    if not url:
        print "Error! Unable to find URL for project %s"
    os.chdir("..")

def checkout(proj):
    print "Checking out %s" % (proj)
    svncheckout = subprocess.call(["svn", "checkout", externals[proj], proj])

def run():
    if not os.path.exists("externals.py"):
        print "You must run this script from the thirdparty directory."
        sys.exit(1)
        
    for proj in externals:
        if os.path.exists(proj):
            update(proj)
        else:
            checkout(proj)

if __name__ == "__main__":
    run()
