#!/usr/bin/python

# Copyright (C) 2006, Matt Sullivan <matts@zarrf.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

longdesc = """
Library providing a distributed message passing system in Python.  Attempts to be as simple to use as possible with little boilerplate code.  Provides safe, efficient object serialization (not using pickle) and message routing.
"""

try:
    from setuptools import setup
    
except ImportError:
    from distutils.core import setup

setup(name = "spoonrpc",
      version = "0.1",
      description = "Distributed message passing IPC system",
      author = "Matt Sullivan",
      author_email = "matts at zarrf com",
      url = "http://www.zarrf.com/SpoonRPC",
      packages = [ 'spoon', "spoon.ber", "spoon.messaging", "spoon.routing", "spoon.transports" ],
      download_url = 'http://www.zarrf.com/SpoonRPC/SpoonRPC-0.1.tar.gz',
      license = 'MIT',
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Topic :: Internet", 
      "Topic :: Software Development :: Object Brokering"],

      long_description = longdesc,
      )

