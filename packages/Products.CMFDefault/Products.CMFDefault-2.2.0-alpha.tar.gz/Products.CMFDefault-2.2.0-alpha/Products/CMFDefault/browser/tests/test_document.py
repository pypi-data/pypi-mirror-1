##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Test Products.CMFDefault.browser.document

$Id: test_document.py 105588 2009-11-12 21:21:32Z jens $
"""

import unittest
from Testing import ZopeTestCase

from Products.CMFDefault.browser.tests.utils import clearVocabulary
from Products.CMFDefault.browser.tests.utils import setupVocabulary
from Products.CMFDefault.testing import FunctionalLayer


ftest_suite = ZopeTestCase.FunctionalDocFileSuite(
                'document.txt',
                setUp=setupVocabulary,
                tearDown=clearVocabulary,
               )
ftest_suite.layer = FunctionalLayer

def test_suite():
    return unittest.TestSuite((
        ftest_suite,
    ))
