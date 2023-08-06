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
from zope import schema, interface
from zope.component import queryUtility
from zope.configuration import fields

from zope.component.zcml import handler
from zope.interface.verify import verifyObject
from zope.app.publisher.browser.resourcemeta import allowed_names
from zope.security.checker import CheckerPublic, NamesChecker
from zope.app.publisher.browser.metadirectives import \
    IBasicResourceInformation

from zope.publisher.interfaces.browser import \
    IDefaultBrowserLayer

from falkolab.resource.interfaces import IResourceType, IResourceFactory

class IResourcePackageDirective(IBasicResourceInformation):
    """ falkolab:resourcePackage directive """

    name = schema.TextLine(
        title=u"The name of the resource package",
        description=u"""
        This is the name used in resource urls. Resource urls are of
        the form site/@@/packagename/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.
        Can't be two packages with same name.""",
        required=True,
        )

    include = fields.Tokens(
        title=u"Include",
        description=u"The resources which this package contains.",
        required=True,
        value_type=schema.Text(),
        )

def resourcePackageDirective(_context, name, include, layer=IDefaultBrowserLayer,
                      permission='zope.Public'):
    if permission == 'zope.Public':
            permission = CheckerPublic

    checker = NamesChecker(allowed_names, permission)
    resourceType = queryUtility(IResourceType, name='package')

    resourceFactory = resourceType(include, checker, name)

    if not verifyObject(IResourceFactory, resourceFactory):
        raise TypeError('Resource factory must provide falkolab.resource.interfaces.IResourceFactory interface')


    handler('registerAdapter',
            resourceFactory, (layer,), interface.Interface, name, _context.info)