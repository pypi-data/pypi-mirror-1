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
$Id: zrtresourcetype.py 200 2009-03-11 08:29:13Z falko $
"""
from zope import interface
from falkolab.resource.interfaces import IExtensibleResourceFactory, IResource
from z3c.zrtresource import ZRTFileResource, ZRTFileResourceFactory
from falkolab.resource.resourcetypes import FileResource, File
from zope.schema.fieldproperty import FieldProperty

from z3c.zrtresource import processor, replace
from zope.app.component.hooks import getSite

class ZRTResource(ZRTFileResource,FileResource):
    interface.implements(IResource)
   
    def GET(self):
        data = self._commands+'\n'+super(FileResource, self).GET()   
        
        p = processor.ZRTProcessor(data, commands={'replace': replace.Replace})
        return p.process(getSite(), self.request)

        

class ZRTResourceFactory(ZRTFileResourceFactory):
    interface.implements(IExtensibleResourceFactory)
    properties = FieldProperty(IExtensibleResourceFactory['properties'])

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):        
        resource = ZRTResource(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        resource._commands = self.properties and self.properties.get('zrt-commands','') or ''
        return resource