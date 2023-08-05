#
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

__author__ = "Matt Sullivan <matts@zarrf.com>"
__date__ = "22 Nov 2006"
__version__ = "0.1.1"
__version_info__ = (0,1,1)
__license__ = "MIT/X Consortium"


from spooncore import Serial, serialprop, lazyprop
from spooncore import SPOONLINKMSG_TAG as __SPOONLINKMSG_TAG__, SPOONNETMSG_TAG as __SPOONNETMSG_TAG__
from spoonstream import SpoonStream
from nulllogger import NullLogger
from objTypes import *

for x in [Serial, serialprop, lazyprop, SpoonStream, NullLogger]:
    x.__module__ = "spoon"

import messaging
import routing
import transports
import ber

messaging.__module__ = "spoon"
routing.__module__ = "spoon"
transports.__module__ = "spoon"
ber.__module__ = "spoon"

__all__ = ["Serial", 
           "serialprop", 
           "lazyprop",
           "SpoonStream",
           "NullLogger",
           "messaging",
           "routing",
           "transports",
           "ber"]



