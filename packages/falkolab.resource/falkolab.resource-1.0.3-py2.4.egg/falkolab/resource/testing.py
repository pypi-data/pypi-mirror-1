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
'''
Created on 03.06.2009

@author: falko
'''
from zope.app.testing import setup
from falkolab.resource.util import ResourceTypesVocabulary


def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}
    from zope.schema.vocabulary import getVocabularyRegistry
    registry = getVocabularyRegistry()
    registry.register('falkolab.resource.AvailableResourceTypes', ResourceTypesVocabulary)
    
def tearDown(test):
    setup.placefulTearDown()