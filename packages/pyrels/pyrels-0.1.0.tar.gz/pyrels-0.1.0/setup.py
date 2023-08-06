#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
from distutils.core import setup

sys.path.insert(0, "src")


__version__ = "0.1.0"
__license__ = "GNU General Public Licence v3 (GPLv3)"
__author__ = "Dinu Gherman"
__date__ = "2008-07-08"


setupCommand = sys.argv[1]


# first try converting README from ReST to HTML, if Docutils is installed
# (else issue a warning)

if setupCommand in ("sdist", "build"):
    toolName = "rst2html.py"
    res = os.popen("which %s" % toolName).read().strip()
    if res.endswith(toolName):
        cmd = "%s '%s' '%s'" % (res, "README.txt", "README.html")
        print "running command %s" % cmd
        cmd = os.system(cmd)
    else:
        print "Warning: No '%s' found. 'README.{txt|html}'" % toolName,
        print "might be out of synch."


# description for Distutils to do its business

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "pyrels",
    version = __version__,
    description = "A tool for displaying relationships between Python objects.",
    long_description = """\
`Pyrels` is a tool for exploring and visualizing relationships between 
Python objects. It does so by analysing and converting Python namespaces 
into `GraphViz <http://www.graphviz.org>`_ files in the 
`DOT <http://www.graphviz.org/doc/info/lang.html>`_ format. 
That means it displays relationships like references between Python names 
and the objects they point to, as well as containment between Python 
container objects (lists, tuples and dictionaries) and the respective 
objects they contain.

At the moment `pyrels` is best used on Python data structures, but it is 
intended to develop it further so that it can also display other types of  relationships like inheritance, module imports, etc. 

One target group for `pyrels` are article and/or book authors who wish to 
illustrate Python data structures graphically without spending a lot of 
time for creating these illustrations manually. `Pyrels` can help you 
automate this process.""",
    date = __date__,
    author = __author__,
    author_email = "gherman@darwin.in-berlin.de",
    maintainer = __author__,
    maintainer_email = "gherman@darwin.in-berlin.de",
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["visualizing", "Python", "relationships", "references", "namespaces"],
    url = baseURL,
    download_url = baseURL + "tmp/pyrels-%s.tar.gz" % __version__,
    package_dir = {"pyrels": "src/pyrels"},
    packages = ["pyrels"],
    scripts = ["scripts/pyrels"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)

