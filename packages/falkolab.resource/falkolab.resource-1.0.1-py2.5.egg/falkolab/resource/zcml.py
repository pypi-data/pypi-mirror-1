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
$Id: zcml.py 200 2009-03-11 08:29:13Z falko $
"""
from falkolab.resource.util import _findResourceType

from warnings import warn
from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope import schema, interface, component
from zope.configuration import fields
from zope.component.zcml import handler
from zope.interface.verify import verifyObject
from zope.app.publisher.browser.metadirectives import IBasicResourceInformation
from zope.app.publisher.browser.resourcemeta import allowed_names
from zope.publisher.interfaces.browser import IDefaultBrowserLayer,\
    IBrowserRequest
from zope.security.checker import CheckerPublic, NamesChecker

from falkolab.resource.interfaces import IResourceType, IResourceFactory,\
    IResourcePropertyManager, IExtensibleResourceFactory
from falkolab.resource.resourcetypes import ResourceType

class IResourceDirective(IBasicResourceInformation):
    """ falkolab:resource directive """

    name = schema.TextLine(
        title = u"The name of the resource",
        description = u"""
        This is the name used in resource urls. Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.
        Can't be two resources with same name.""",
        required = True)

    type = schema.TextLine(
        title = u'Resource type',
        required = False)

    src = fields.Path(
        title = u'Resource source',
        description = u'Resource source specific for resource type (for example file path for file resource)',
        required = True)



class IResourcePropertyDirective(interface.Interface):
    name = schema.TextLine(
        title = u'Resource option name',
        required = True)

    value = schema.TextLine(
        title = u'Resource option value',
        required = True)

class IResourceTypeDirective(interface.Interface):
    """ Resource type factory """
    name = schema.TextLine(
        title = u'Resource type name',
        description = u'Used for ''type'' field of resource directive',
        required = True)

    description = schema.TextLine(
        title = u'Resource type description',
        description = u'Used for describe type of resource directive',
        required = False)

    mask = fields.Tokens(
                  title=u"Specifications this names are the reserved for",
                  description=u"List of strings is the file name extension or file name that the handler processes (e.g: *_res.pt *.jpg my[0-9].resource)",
                  value_type=schema.TextLine(),
                  required=False,
                  unique=True,
                  #default=['*.*']
                  )

    factory =fields.GlobalObject(
        title = u'Resource Type Factory',
        description = u'Custom resource type factory',
        required = True
        )

def _setProperty(resourceFactory, name, value):
    resmgr = component.queryAdapter(resourceFactory, IResourcePropertyManager, name, default=None)
    if not resmgr:
        resmgr = component.queryAdapter(resourceFactory, IResourcePropertyManager, default=None)

    if resmgr:
        resmgr.setProperty(name, value)
    else:
        warn(u"Can't find IResourcePropertyManager adapter for resource '%s' to set property '%s'.%s %s" %(self.name, name, str(self.resourceFactory),str(resmgr)))
   
   
class ResourceDirective(object):

    def __init__(self, _context, name, src, layer=IDefaultBrowserLayer,
                      permission='zope.Public', type=''):
        if permission == 'zope.Public':
            permission = CheckerPublic

        checker = NamesChecker(allowed_names, permission)
        resourceType = None
        self.name = name
        self.layer = layer

        if type:
            resourceType = queryUtility(IResourceType, name=type)
        else:
            resourceType=_findResourceType(src, default=u'file')

        if resourceType==None:
            raise ComponentLookupError("Can't find resource type for resource '%s' from source '%s'" %(name, src))

        resourceFactory = resourceType(src, checker, name)
        resourceFactory.typeName = resourceType.getName()

        if not verifyObject(IResourceFactory, resourceFactory):
            raise TypeError('Resource factory must provide IResourceFactory interface')
        
        _context.action(
                discriminator = ('resource', name, IBrowserRequest, layer),
                callable = handler,
                args = ('registerAdapter',
                        resourceFactory, (layer,), interface.Interface, name, _context.info),
                )

        self.resourceFactory = resourceFactory

    def property(self, _context, name, value):
        if IExtensibleResourceFactory.providedBy(self.resourceFactory):
            _context.action(
                discriminator = ('resource.property', self.name, name, IBrowserRequest, self.layer),
                callable = _setProperty,
                args = (self.resourceFactory, name, value)
                )            
        else:
            warn(u"Resource factory for resource '%s' must implement IExtensibleResourceFactory" %self.name)

 

def resourceTypeDirective(_context, name, factory, description='', mask=None):

    if not IResourceFactory.implementedBy(factory):
        raise TypeError("Must implement IResourceFactory")

    resourceType = ResourceType(factory, name, mask)

    handler('registerUtility', resourceType, IResourceType, name)

