#!/home/jim/p/z4i/jim-icu/var/opt/python/bin/python -u
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Run tests in a Zope instance home.

$Id: test.py 40612 2005-12-06 20:52:16Z jim $
"""
import sys
sys.path.insert(0, 'src')
from zope.testing import testrunner

defaults = '--test-path src -szope.ucol'.split()

status = testrunner.run(defaults)

sys.exit(status)
