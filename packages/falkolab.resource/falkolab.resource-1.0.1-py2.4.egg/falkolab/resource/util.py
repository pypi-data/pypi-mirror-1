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
$Id: util.py 200 2009-03-11 08:29:13Z falko $
"""
from zope import interface, component
from falkolab.resource.interfaces import IAvailableResourceTypes, IResourceType
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.component.interfaces import ComponentLookupError

class AvailableResourceTypes(object):
    interface.implements(IAvailableResourceTypes)

    @property
    def resourceTypes(self):
        reglist = component.getUtilitiesFor(IResourceType)
        for name, resourceType in reglist:
            yield name

def resourceTypesVocabulary(context):
    utility = component.getUtility(IAvailableResourceTypes)
    return SimpleVocabulary.fromValues(utility.resourceTypes)

interface.alsoProvides(resourceTypesVocabulary, IVocabularyFactory )


def _findResourceType(path, allowed=None, default=None):
    """Find first match resourceType by name. Optionally use allowed type names.
    Default resource name used if not find
    """

    if allowed and default and (default not in allowed):
        raise ValueError(u'default resource type name must be in allowed list')

    if allowed:
        reglist = [(name, component.getUtility(IResourceType, name=name)) for name  in allowed]
    else:
        reglist = component.getUtilitiesFor(IResourceType)


    for name, resourceType in reglist:
        if resourceType.matchName(path):
            return resourceType

    resourceType = None

    if default:
        resourceType = component.queryUtility(IResourceType, name=default)

        if resourceType==None:
            raise ComponentLookupError(u"Can't find resource type '%s'" % default)

    return resourceType