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
$Id: adapters.py 200 2009-03-11 08:29:13Z falko $
"""
from zope import interface, component
from falkolab.resource.interfaces import IResourcePropertyManager, \
IResourceContainerFactory, IExtensibleResourceFactory, IResourceType
from zope.configuration.exceptions import ConfigurationError


class DefaultResourceTypePropertyAdapter(object):
    interface.implements(IResourcePropertyManager)
    component.adapts(IExtensibleResourceFactory)

    def __init__(self, context):
        if context==None:
            raise ValueError("Can't be None")

        self.context = context

    def setProperty(self, name, stringValue):
        if not name:
            raise ValueError("Property name can't be empty or None")
        if not stringValue:
            raise ValueError("Property value can't be empty or None")

        resourceFactory = self.context

        if resourceFactory.properties == None:
            resourceFactory.properties = {}

        resourceFactory.properties[name]=stringValue

class ResourceTypePropertyAdapter(object):
    interface.implements(IResourcePropertyManager)
    component.adapts(IResourceContainerFactory)

    propertyName='types'

    def __init__(self, context):
        if context==None:
            raise ValueError("Can't be None")

        self.context = context


    def setProperty(self, name, stringValue):
        if self.propertyName != name:
            return

        resourceFactory = self.context

        if not stringValue:
            resourceFactory.types = []
            return

        if resourceFactory.types == None:
            resourceFactory.types = []

        types = []

        for typeName in stringValue.split():
            if component.queryUtility(IResourceType, typeName) == None:
                raise ConfigurationError("Can't find resource type '%s'" % typeName)
            if not typeName in types:
                types.append(typeName)

        resourceFactory.types=types

