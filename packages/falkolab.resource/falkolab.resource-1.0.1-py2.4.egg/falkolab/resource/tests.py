# -*- coding: utf-8 -*-
##############################################################################
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
"""
$Id: tests.py 200 2009-03-11 08:29:13Z falko $
"""
import os
import doctest, unittest

from zope.configuration import xmlconfig
from zope.app.testing import functional
from zope import interface
from falkolab.resource import resourcetypes
from falkolab.resource.interfaces import IResourceFactory

class CustomResource(resourcetypes.FileResource):
    pass

class CustomFileResourceFactory(resourcetypes.FileResourceFactory):
    interface.implements(IResourceFactory)

    options = {}
    def __call__(self, request):
        resource = CustomResource(self._file, request)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource

def zcml(s, execute=True):
    """ZCML registration helper"""
    from zope.app.appsetup.appsetup import __config_context as context
    try:
        xmlconfig.string(s, context, execute=execute)
    except:
        context.end()
        raise

ResourceFunctionalLayer = functional.ZCMLLayer(
   os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
  __name__, 'ResourceFunctionalLayer')

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        'README.txt',
        globs={'zcml': zcml},
        optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
        )
    suite.layer = ResourceFunctionalLayer

    suite2 = functional.FunctionalDocFileSuite(
        'package/package.txt',
        globs={'zcml': zcml},
        optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
        )
    suite2.layer = ResourceFunctionalLayer

    return unittest.TestSuite((
        suite,
        suite2,
        doctest.DocTestSuite('falkolab.resource.resourcetypes'),
        doctest.DocTestSuite()
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

#TODO: Написать тесты по расширению ресурсов