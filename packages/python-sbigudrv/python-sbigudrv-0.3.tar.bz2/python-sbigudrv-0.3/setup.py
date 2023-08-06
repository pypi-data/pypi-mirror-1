#! /usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright 2008 Paulo Henrique Silva <ph.silva@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages, Extension
from pkg_resources import require, resource_filename

import platform
import sys
from subprocess import Popen, PIPE

def get_num_include_path ():
    numpy = None

    try:
        numpys = require('numpy >= 1.0.3')
    except Exception:
        return False

    if not numpys:
        print >> sys.stderr, "Cannot find numpy installation."
        exit(-1)
    else:
        numpy = numpys[0]

    return resource_filename(numpy.project_name, 'core/include')

def getPythonArch ():
    if "64" in platform.architecture()[0]:
        return "64"
    return "32"

#
# general cheks
#

# platform
if sys.platform == "win32":
    print """
==================================================================
This package is not supported on Win32 system yet. Try it on Linux
please, or contact the author about porting it to Windows too.
===================================================================
"""
    sys.exit(1)


# SWIG

HAVE_SWIG=True

if "install" in sys.argv or "build" in sys.argv or "bdist_egg" in sys.argv:
    try:
        Popen(["swig"], stdout=PIPE, stderr=PIPE).wait()
    except OSError:
        HAVE_SWIG=False
        print """
=======================================================================
It seems like you doesn't have SWIG, I'll try to use a pre-compiled
wrapper. If you see any problem below, install a SWIG version and try
again.

You can get SWIG at http://www.swig.org or using your distribution
packager, like apt-get on Debians or yum in RPM based distros.
=======================================================================
"""

# Numpy before installation
if not get_num_include_path():
    print """
=======================================================================
This script requires numpy before they start any command, so, the first
time you run it without a valid numpy installation it will take a
while to download numpy. Please wait patientily. Once you have numpy
downloaded it will go as fast as you want.
=======================================================================
"""
    setup(name="python-sbigudrv")

#
# setup
#

ENV_LINUX = 7
SBIG_UDRV_VERSION="4.57"
SBIG_UDRV_ARCH=getPythonArch()

# if we don't have SWIG, try with pre-compiler wrapper
extension_src = None

if HAVE_SWIG:
    extension_src = ["sbigudrv/sbigudrv.i"]
else:
    extension_src = ["sbigudrv/sbigudrv_wrap.c"]

# go!
setup(name="python-sbigudrv",

      ext_modules      = [Extension("sbigudrv/_sbigudrv", extension_src, 
                                    swig_opts=["-python", "-I./sbigudrv", "-DTARGET=%d" % ENV_LINUX],
                                    include_dirs=[get_num_include_path(), './sbigudrv'],
                                    define_macros=[('TARGET', ENV_LINUX)],
                                    libraries=["usb"],
                                    extra_link_args=["./sbigudrv/libsbigudrv-%s-linux-amd%s.a" % (SBIG_UDRV_VERSION,
                                                                                                  SBIG_UDRV_ARCH)])],

      packages         = find_packages(),
      include_package_data = True,

      zip_safe         = False,

      version          = "0.3",
      description      = "Python wrappers for SBIG (tm) Universal Driver",
      long_description = open("README").read(),
      author           = "Paulo Henrique Silva",
      author_email     = "ph.silva@gmail.com",
      license          = "Apache License 2.0",
      url              = "http://code.google.com/p/python-sbigudrv",
      classifiers      = [ 'Development Status :: 4 - Beta',
                           'Environment :: Console',
                           'Intended Audience :: Science/Research',
                           'Intended Audience :: Developers',
                           'License :: OSI Approved :: Apache Software License',
                           'Natural Language :: English',
                           'Operating System :: POSIX :: Linux',
                           'Programming Language :: Python',
                           'Topic :: Scientific/Engineering :: Astronomy',
                           'Topic :: Software Development :: Libraries :: Python Modules']
      )
