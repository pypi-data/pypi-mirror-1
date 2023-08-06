# -*- coding: utf-8 -*- ######################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################

import os
import doctest, unittest

from zope.configuration import xmlconfig
from zope.app.testing import functional

def zcml(s, execute=True):
    """ZCML registration helper"""
    from zope.app.appsetup.appsetup import __config_context as context
    try:
        xmlconfig.string(s, context, execute=execute)
    except:
        context.end()
        raise

ExtJsLayerFunctionalLayer = functional.ZCMLLayer(
   os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
  __name__, 'ExtJsLayerFunctionalLayer')

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        'README.txt',
        globs={'zcml': zcml},
        optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
        )
    suite.layer = ExtJsLayerFunctionalLayer

    return unittest.TestSuite((
        suite,
        doctest.DocTestSuite()    
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
