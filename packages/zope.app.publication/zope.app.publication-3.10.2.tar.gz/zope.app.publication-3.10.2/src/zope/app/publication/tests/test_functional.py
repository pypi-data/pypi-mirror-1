##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test not found errors

$Id: test_functional.py 107890 2010-01-08 22:36:05Z faassen $
"""

import re
import unittest
from zope.testing import renormalizing
from zope.app.testing import functional
from zope.app.publication.testing import PublicationLayer


checker = renormalizing.RENormalizing([
    (re.compile(r"HTTP/1\.([01]) (\d\d\d) .*"), r"HTTP/1.\1 \2 <MESSAGE>"),
    ])


def test_suite():
    methodnotallowed = functional.FunctionalDocFileSuite(
        '../methodnotallowed.txt')
    methodnotallowed.layer = PublicationLayer
    httpfactory = functional.FunctionalDocFileSuite(
        '../httpfactory.txt', checker=checker)
    httpfactory.layer = PublicationLayer
    site = functional.FunctionalDocFileSuite(
        '../site.txt')
    site.layer = PublicationLayer
    return unittest.TestSuite((
        methodnotallowed,
        httpfactory,
        site,
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

