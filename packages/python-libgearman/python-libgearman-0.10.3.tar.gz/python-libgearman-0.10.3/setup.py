#!/usr/bin/env python
# -*- mode: python; c-basic-offset: 2; indent-tabs-mode: nil; -*-
#  vim:expandtab:shiftwidth=2:tabstop=2:smarttab:
#  gearman-interface: Interface Wrappers for Gearman
#  Copyright (c) 2009 Monty Taylor
#  All rights reserved.
# 
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
# 
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. The name of the author may not be used to endorse or promote products
#     derived from this software without specific prior written permission.
# 
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

from distutils.command.clean import clean
from distutils.command.build import build
from setuptools import setup,Extension
import os.path, os
import sys
from gearman.release import version

description = """Python wrapper of libgearman"""

classifiers="""\
Development Status :: 2 - Pre-Alpha
License :: OSI Approved :: BSD License
Operating System :: POSIX :: Linux
Programming Language :: C++
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

setup(name="python-libgearman",
      version=version,
      description=description,
      long_description=description,
      author="Monty Taylor",
      author_email="mordred@inaugust.com",
      url="http://launchpad.net/gearman-interface",
      platforms="linux",
      license="GPL",
      classifiers=filter(None, classifiers.splitlines()),

      ext_modules=[
        Extension("gearman._libgearman",
                  sources=["libgearman.c"],
                  libraries=["gearman"],
                  ),
        ],
      #test_suite = "tests.AllTests.test_all",
      packages=["gearman"],
      )

