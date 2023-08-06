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
$Id: interfaces.py 200 2009-03-11 08:29:13Z falko $
"""
from zope import interface, schema

class IResourceFactory(interface.Interface):

    def __init__(path, checker, name):
        pass

    def __call__(request):
        """Create resource"""

class IExtensibleResourceFactory(IResourceFactory):
    properties = schema.Dict(
                          title = u'Resource properties',
                          description = u'Resource specific properties dictionary',
                          key_type = schema.TextLine(),
                          value_type = schema.TextLine(),
                          default = {}
                          )


class IResourceContainerFactory(IExtensibleResourceFactory):
    types = schema.List(
                        title=u"Types",
                        description=u"List of allowed types for contained resources",
                        required=False,
                        unique=True,
                        value_type = schema.Choice(\
                                    vocabulary='falkolab.resource.AvailableResourceTypes'),
                        default = []
                        #value_type=schema.TextLine(title=u"Resource type")
                        )

class IResource(interface.Interface):

    def renderHtmlEmbeding(request, **kwargs):
        pass

class IResourceType(interface.Interface):

    def __init__(factory, name, mask=None):
        pass

    def __call__( path, checker, name):
        """ create resource factory """

    def matchName(name):
        pass

    def getName():
        pass

    def getMasks():
        pass

class IAvailableResourceTypes(interface.Interface):
    resourceTypes = schema.Iterable(
                                    title=u"Registered resource types",
                                    description=u"A list of registered resource types",
                                    )


class IResourcePropertyManager(interface.Interface):
    """Set up property value from zcml property subdirective"""

    def setProperty(name, stringValue):
        """Set raw string property value"""





