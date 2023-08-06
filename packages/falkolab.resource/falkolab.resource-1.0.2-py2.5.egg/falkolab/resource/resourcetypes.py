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
$Id: resourcetypes.py 200 2009-03-11 08:29:13Z falko $
"""
from falkolab.resource.interfaces import IResourceType, IResource,\
    IResourceContainerFactory, IExtensibleResourceFactory
from zope.schema.fieldproperty import FieldProperty
from falkolab.resource.util import _findResourceType

import os, fnmatch
from zope import interface

from zope.configuration.exceptions import ConfigurationError
from zope.exceptions.interfaces import DuplicationError

from zope.component.factory import Factory

from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.publisher.browser.fileresource import FileResource as FileResource_
from zope.app.publisher.browser.pagetemplateresource import \
    PageTemplateResource as PTResource, \
    PageTemplateResourceFactory as PTResFactory
from zope.app.publisher.browser.directoryresource import _marker, Directory
from zope.app.publisher.browser.resource import Resource
from zope.app.publisher.browser.resources import empty

from zope.app.publisher.fileresource import Image, File as File_


class File(File_):

    def __init__(self, path, name):
        super(File, self).__init__(path, name)
        """There has always been confusion on the official MIME type of javascript.
        While servers mostly seem to use the following Apache rule: AddType application/x-javascript .js
        authors claim it is text/javascript in the TYPE attribute of the SCRIPT element (if they declare it).
        That has multiple reasons. First of all, the HTML specification suggests text/javascript and
        application/x-javascript is not supported by Internet Explorer.
        Note that IE does not support it only if it is the value of the TYPE attribute,
        what the server sends does not seem to matter."""
        if self.content_type == 'application/x-javascript':
            self.content_type = 'text/javascript'

class FileResource(FileResource_):
    interface.implements(IResource)

    def renderHtmlEmbeding(self, request, **kwargs):
        path = self.context.path

        if  path.endswith('.js'):
            return u'<script type="text/javascript" src="%s"></script>' %self()
        elif  path.endswith('.css'):
            return u'<link rel="stylesheet" type="text/css" media="screen" href="%s" />' %self()
        else:
            return u'<!-- not support embeding -->'

class FileResourceFactory(object):
    interface.implements(IExtensibleResourceFactory)
    properties = FieldProperty(IExtensibleResourceFactory['properties'])


    def __init__(self, path, checker, name):
        self._file = File(path, name)
        self._checker = checker
        self._name = name
        self.properties = {}

    def __call__(self, request):
        resource = FileResource(self._file, request)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource

class ImageResourceFactory(object):
    interface.implements(IExtensibleResourceFactory)
    properties = FieldProperty(IExtensibleResourceFactory['properties'])

    def __init__(self, path, checker, name):
        self._file = Image(path, name)
        self._checker = checker
        self._name = name
        self.properties={}

    def __call__(self, request):
        resource = FileResource(self._file, request)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource

class PageTemplateResource(PTResource):
    interface.implements(IResource)

    def renderHtmlEmbeding(self, request, **kwargs):
        return u'<!-- not supported embeding -->'

class PageTemplateResourceFactory(PTResFactory):
    interface.implements(IExtensibleResourceFactory)

    properties = FieldProperty(IExtensibleResourceFactory['properties'])

    def __init__(self, path, checker, name):
        super(PageTemplateResourceFactory, self).__init__(path, checker, name)
        self.properties = {}

    def __call__(self, request):
        resource = PageTemplateResource(self.__pt, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource

class DirectoryResource(BrowserView, Resource):

    interface.implements(IBrowserPublisher, IResource)


    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        return self.get(name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return empty, ()

    def __getitem__(self, name):
        res = self.get(name, None)
        if res is None:
            raise KeyError(name)
        return res

    def get(self, name, default=_marker):
        path = self.context.path

        filename = os.path.join(path, name)
        isfile = os.path.isfile(filename)
        isdir = os.path.isdir(filename)


        if not (isfile or isdir):
            if default is _marker:
                raise NotFound(None, name)
            return default

        rname = os.path.join(self.__name__, name)

        if isfile:
            if self.types and 'file' not in self.types:
                defaultType=None
            else:
                defaultType='file'

            resourceType = _findResourceType(os.path.normcase(name), self.types, defaultType)
            if resourceType is None:
                raise NotFound(self, name)
            resource = resourceType(filename, self.context.checker, rname)(self.request)
        else:
            resource = DirectoryResourceFactory(filename, self.context.checker, rname)(self.request)
            if self.types:
                resource.types = self.types

        resource.__parent__ = self
        return resource

    def renderHtmlEmbeding(self, request, **kwargs):
        return u'<!-- not supported embeding -->'



class DirectoryResourceFactory(object):
    interface.implements(IResourceContainerFactory)

    properties = FieldProperty(IResourceContainerFactory['properties'])
    types = FieldProperty(IResourceContainerFactory['types'])

    def __init__(self, path, checker, name):
        super(DirectoryResourceFactory, self).__init__()
        self.properties = {}
#        for type in ['file', 'zpt', 'image', 'directory']:
#            self.types.append(type)


        if not os.path.isdir(path):
            raise ConfigurationError("Directory %s does not exist" % path)

        data =  checker.get_permissions
        permission_id = data.items()[0][1]
        for n in  ('__getitem__', 'get'):
            if data.get(n, permission_id) is not permission_id:
                raise DuplicationError(n)
            data[n] = permission_id

        self.__dir = Directory(path, checker, name)
        self.__name = name
        self.__checker = checker


    def __call__(self, request):
        resource = DirectoryResource(self.__dir, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name

        resource.types = self.types

        return resource

class ResourceType(Factory):
    """
    Creates resource factories

    >>> class TestResFactory(object):
    ...     def __call__(self, teststring):
    ...        print teststring
    ...
    >>> rt = ResourceType(TestResFactory(), 'mytype')
    >>> rt('123')
    123
    >>> rt.getName()
    'mytype'
    >>> rt.matchName('script.js')
    False
    >>> rt = ResourceType(TestResFactory(), 'mytype', ['*.js'] )
    >>> rt.getMasks()
    ('*.js',)
    >>> rt.matchName('script.js')
    True
    >>> rt.matchName('script.css')
    False
    >>> rt = ResourceType(TestResFactory(), 'mytype', ['*?123.js'] )
    >>> rt.matchName('script.js') and rt.matchName('123.js')
    False
    >>> rt.matchName('script123.js')
    True
    >>> rt = ResourceType(TestResFactory(), 'mytype', ['*.js','*.css'] )
    >>> rt.matchName('script.js') and rt.matchName('script.css')
    True
    """
    interface.implements(IResourceType)

    __name = ''
    __mask = ''

    def __init__(self, callable, name, mask=None):
        super(ResourceType, self).__init__(callable)
        self.__mask = mask
        self.__name = name

    def matchName(self, name):
        """To test is the given name matches the resource type mask"""
        if self.__mask is None:
            return False

        for m in self.__mask:
            if fnmatch.fnmatch(name, m):
                return True

        return False

    def getName(self):
        return self.__name

    def getMasks(self):
        if self.__mask:
            return tuple(self.__mask)
        else:
            return ()




