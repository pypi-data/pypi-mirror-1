##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Versioned Resources Test Setup

$Id: test_doc.py 89405 2008-08-05 16:58:50Z srichter $
"""
__docformat__ = "reStructuredText"
import unittest
from zope.testing import doctest
from zope.app.testing import placelesssetup
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class ITestLayer(IDefaultBrowserLayer):
    pass

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            '../README.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ))
