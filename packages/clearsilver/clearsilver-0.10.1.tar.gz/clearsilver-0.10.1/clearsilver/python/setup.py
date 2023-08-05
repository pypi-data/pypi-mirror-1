#!/usr/bin/env python

import os, string, re, sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages, Extension
#from distutils.core import setup, Extension

VERSION = "0.10.1"
INC_DIRS = ["../"]
LIBRARIES = ["neo_cgi", "neo_cs", "neo_utl"]
LIB_DIRS = ["../libs"]

## ARGGH!!  It looks like you can only specify a single item on the
## command-line or in the setup.cfg file for options which take multiple
## lists... and it overrides what is defined here.  So I have to do all
## the work of the configure file AGAIN here.  At least its in python,
## which is easier...
## Actually, forget that, I'm just going to load and parse the rules.mk
## file and build what I need

if not os.path.exists("../rules.mk"):
  cmd = "cd ..; configure; make"
  os.system(cmd)

#  raise "You need to run configure first to generate the rules.mk file!"

make_vars = {}
rules = open("../rules.mk").read()
for line in string.split(rules, "\n"):
  parts = string.split(line, '=', 1)
  if len(parts) != 2: continue
  var, val = parts
  var = string.strip(var)
  make_vars[var] = val
  if var == "CFLAGS":
    matches = re.findall("-I(\S+)", val)
    inserted = []
    for inc_path in matches:
      # inc_path = match.group(1)
      if inc_path not in INC_DIRS:
      	inserted.append(inc_path)
	sys.stderr.write("adding inc_path %s\n" % inc_path)
    INC_DIRS = inserted + INC_DIRS
  elif var == "LIBS":
    matches = re.findall("-l(\S+)", val)
    inserted = []
    for lib in matches:
      # lib = match.group(1)
      if lib not in LIBRARIES:
      	inserted.append(lib)
	sys.stderr.write("adding lib %s\n" % lib)
    LIBRARIES = inserted + LIBRARIES
  elif var == "LDFLAGS":
    matches = re.findall("-L(\S+)", val)
    inserted = []
    for lib_path in matches:
      # lib_path = match.group(1)
      if lib_path not in LIB_DIRS:
      	inserted.append(lib_path)
	sys.stderr.write("adding lib_path %s\n" % lib_path)
    LIB_DIRS = inserted + LIB_DIRS

def expand_vars(vlist, vars):
  nlist = []
  for val in vlist:
    if val[:2] == "$(" and val[-1] == ")":
      var = val[2:-1]
      val = vars.get(val, "")
      if val: nlist.append(val)
    else:
      nlist.append(val)
  return nlist

INC_DIRS = expand_vars(INC_DIRS, make_vars)
LIB_DIRS = expand_vars(LIB_DIRS, make_vars)
LIBRARIES = expand_vars(LIBRARIES, make_vars)

description = """
Clearsilver is a fast, powerful, and language-neutral HTML template system.  It
was designed through years of commercial web development at eGroups.com and
Yahoo!. Clearsilver's speed comes from being written as a C module which is
exported for use in C, C++, Python, Perl, Ruby, and Java. 

The goal of Clearsilver is to get nearly all html, strings, and presentation 
logic out of your code. By drastically reducing code size in your application, 
readability and maintainability are improved. Furthermore, it becomes easier to 
make UI changes without introducing bugs. Clearsilver unifies working with 
cookies, form data, and the http environment, by making it trivial to access 
them from either your code or templates in a standard fashion. It also makes it 
very easy to skin the application, or allow end user UI customization. 

As a bonus, tools designed to work in concert with clearsilver are also 
available, including an object to relational database mapping tool, odb.py, and 
a transparent internationalization system, trans.py.

Enjoy!
"""

setup(name="clearsilver",
      version=VERSION,
      description = "High performance HTML Template System",
      long_description=description,
      author="Brandon Long",
      author_email="blong@fiction.net",
      url="http://www.clearsilver.net/",
      download_url = "http://www.willowmail.com/clearsilver/clearsilver-%s.tar.gz" % VERSION,

      ext_modules=[Extension(
        name="neo_cgi",
	sources=["neo_cgi.c", "neo_cs.c", "neo_util.c"],
	include_dirs=INC_DIRS,
	library_dirs=LIB_DIRS,
	libraries=LIBRARIES,
	)],

      license="Apache",
      keywords=["html templates"],
      classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows :: Windows NT/2000",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Software Development :: Localization",
        "Topic :: Text Processing :: Markup :: HTML"
      ]
      )
