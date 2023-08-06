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
$Id: tests.py 301 2009-08-21 18:46:18Z falko $
"""

import doctest, unittest

from zope import interface
from falkolab.resource import resourcetypes
from falkolab.resource.interfaces import IResourceFactory
from falkolab.resource import testing

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

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(            
            'README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),

        doctest.DocFileSuite(    
            'package/package.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocTestSuite('falkolab.resource.resourcetypes'),     
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')