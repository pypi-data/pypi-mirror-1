##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Javascript Form Framework Interfaces.

$Id: test_doc.py 77926 2007-07-14 13:40:54Z pcardune $
"""
__docformat__ = "reStructuredText"
import unittest
import zope.testing.doctest

from z3c.form import testing

def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(
            '../jsevent.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        zope.testing.doctest.DocFileSuite(
            '../ajax.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        zope.testing.doctest.DocFileSuite(
            '../jsaction.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        zope.testing.doctest.DocFileSuite(
            '../jqueryrenderer.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        zope.testing.doctest.DocFileSuite(
            '../jsvalidator.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        ))
