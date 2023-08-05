#!/usr/bin/env python

# dupfilefind -- find files with identical contents
# 
# Copyright (C) 2007 Zooko Wilcox-O'Hearn
# Author: Zooko Wilcox-O'Hearn
# 
# This file is part of dupfilefind.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version, with the added permission that, if you become obligated
# to release a derived work under this licence (as per section 2.b), you may
# delay the fulfillment of this obligation for up to 12 months.  If you are
# obligated to release code under section 2.b of this licence, you are
# obligated to release it under these same terms, including the 12-month grace
# period clause.  See the COPYING file for details.

try:
    from ez_setup import use_setuptools
except ImportError:
    pass
else:
    import sys
    if 'cygwin' in sys.platform.lower():
        min_version='0.6c6'
    else:
        min_version='0.6a9'
    use_setuptools(min_version=min_version, download_delay=0)

from setuptools import Extension, find_packages, setup

trove_classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: GNU General Public License (GPL)",  # XXX
    "Intended Audience :: Developers", 
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: System Administrators",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Operating System :: POSIX :: Linux",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows :: Windows NT/2000",
    "Operating System :: OS Independent", 
    "Natural Language :: English", 
    "Programming Language :: Python", 
    "Topic :: Utilities",
    "Topic :: System :: Systems Administration",
    "Topic :: System :: Filesystems",
    "Topic :: System :: Archiving :: Backup", 
    "Topic :: System :: Archiving :: Mirroring", 
    "Topic :: System :: Archiving", 
    ]

try:
    import os
    (cin, cout, cerr,) = os.popen3("darcsver")
    print cout.read()
except Exception, le:
    pass
import re
VERSIONFILE = "dupfilefind/_version.py"
verstr = "unknown"
VSRE = re.compile("^verstr = ['\"]([^'\"]*)['\"]", re.M)
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    mo = VSRE.search(verstrline)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("if %s.py exists, it is required to be well-formed" % (VERSIONFILE,))

setup(name='dupfilefind',
      version=verstr,
      description='find files with identical contents',
      long_description='find files with identical contents',
      author='Zooko O\'Whielacronx',
      author_email='zooko@zooko.com',
      url='http://pypi.python.org/pypi/dupfilefind',
      license='GNU GPL', # XXX
      install_requires=["argparse >= 0.8",],
      packages=find_packages(),
      include_package_data=True,
      setup_requires=['setuptools_darcs >= 1.0.4', "pyutil >= 1.3.5",],
      classifiers=trove_classifiers,
      entry_points = { 'console_scripts': [ 'dupfilefind = dupfilefind.cmdline_dupfilefind:main'] },
      zip_safe=False, # I prefer unzipped for easier access.
      )
