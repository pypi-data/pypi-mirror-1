================================================================================
falkolab.resource components
================================================================================

Этот набор компонентов для работы с ресурсами

  >>> from zope import component, interface
  >>> from falkolab.resource import interfaces, resourcetypes

  >>> import falkolab.resource
  >>> import os, os.path

  >>> import tempfile
  >>> scriptFileName =  tempfile.mktemp('script.js')
  >>> open(scriptFileName, 'w').write('script data')
  >>> imageFileName =  tempfile.mktemp('image.jpg')
  >>> open(imageFileName, 'w').write('jpg image data')
  >>> ptFileName =  tempfile.mktemp('template.pt')
  >>> open(ptFileName, 'w').write('zope page template')


Теперь можно зарегистрировать ресурс:

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="resource.js"
  ...       src="%s" />
  ... </configure>
  ... """ % scriptFileName)

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="image-resource"
  ...       src="%s" />
  ... </configure>
  ... """ % imageFileName)

 Посмотрим зарегистрировались ли адаптеры

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> response = request.response

  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='resource.js')

  >>> resource
  <falkolab.resource.resourcetypes.FileResource object at ...>

  >>> isinstance(resource.context, resourcetypes.File)
  True

  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='image-resource')

  >>> resource
  <falkolab.resource.resourcetypes.FileResource object at ...>

  >>> isinstance(resource.context, resourcetypes.Image)
  True



  Можно указать тип ресурса явно

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="image2-resource"
  ...       type="image"
  ...       src="%s" />
  ... </configure>
  ... """ % scriptFileName)

  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='image2-resource')

  >>> isinstance(resource.context, resourcetypes.Image)
  True



Собственные типы ресурсов
================================================================================

Можно определить собственный тип ресурсов. Все что требуется
это определ класс реализующий интерфейс IResourceFactory

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...       <resourceType
  ...           name="custom"
  ...           factory="falkolab.resource.tests.CustomFileResourceFactory" />
  ... </configure>
  ... """)

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="custom-resource"
  ...       type="custom"
  ...       src="%s" />
  ... </configure>
  ... """ %scriptFileName)

  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='custom-resource')

  >>> resource
  <falkolab.resource.tests.CustomResource object at ...>


Подмена типов
================================================================================

Можно перегрузить стандартный тип:

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...       <resourceType
  ...           name="zpt"
  ...           mask="*.pt"
  ...           factory="falkolab.resource.tests.CustomFileResourceFactory" />
  ... </configure>
  ... """)

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="pt-resource"
  ...       src="%s" />
  ... </configure>
  ... """ %ptFileName)

  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='pt-resource')

  >>> resource
  <falkolab.resource.tests.CustomResource object at ...>

  >>> os.unlink(scriptFileName)
  >>> os.unlink(imageFileName)
  >>> os.unlink(ptFileName)

  ZRT resource
================================================================================
Имена ZRT ресурсов должны удовлетворять одной из следующих масок: *.zrt.css *.zrt.js *.zrt
Или вы должны явно указать тип через атрибут: type="zrt" 

  >>> zrtFileName =  tempfile.mktemp('style.zrt.css')
  >>> open(zrtFileName, 'w').write('''\
  ... /* zrt-replace: "foo" "bar" */
  ... foo foo foo foo foo''')

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="zpt-resource"
  ...       src="%s" />
  ... </configure>
  ... """ %zrtFileName)

  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='zpt-resource')

  >>> resource
  <falkolab.resource.zrt.zrtresourcetype.ZRTResource object at ...>

  >>> print resource.GET()
  bar bar bar bar bar
  
  >>> os.unlink(zrtFileName)
  
  Можно указать комманду через поддирективу property, тип ресурса также можно 
  указать если его нельзя определить по расширению файла 
  
  >>> zrtFileName =  tempfile.mktemp('style.css')
  >>> open(zrtFileName, 'w').write('''\
  ... foo foo foo foo foo''')
  
  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...   <resource
  ...       name="zpt-resource-with-property"
  ...       src="%s"
  ...       type="zrt">
  ...       <property 
  ...            name="zrt-commands"
  ...            value='/* zrt-replace: "foo" "muu" */' />
  ...   </resource>  
  ... </configure>
  ... """ %zrtFileName)
  
  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='zpt-resource-with-property')

  >>> print resource.GET()
  muu muu muu muu muu  

  >>> os.unlink(zrtFileName)


  Directory resource
================================================================================

  >>> import tempfile
  >>> dirName = tempfile.mkdtemp()
  >>> os.mkdir(os.path.join(dirName, 'subfolder'))
  >>> open(os.path.join(dirName, 'script.js'), 'w').write('script data')
  >>> open(os.path.join(dirName, 'style.css'), 'w').write('style data')
  >>> open(os.path.join(dirName, 'image.png'), 'w').write('png image data')

Можно зарегистрировать директорию с ресурсами и указать
допустимые типы ресурсов.

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...       <resource
  ...           name="resdir"
  ...           type="directory"
  ...           src="%s" />
  ...
  ... </configure>
  ... """ %(dirName + '_'))
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: ...
        ConfigurationError: Directory ... does not exist


  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...       <resource
  ...           name="resdir"
  ...           type="directory"
  ...           src="%s" />
  ...
  ... </configure>
  ... """ %dirName)


  >>> dirResource = component.getAdapter(
  ...    request, interface.Interface, name='resdir')
  >>> dirResource
  <falkolab.resource.resourcetypes.DirectoryResource object at ...>

  >>> dirResource.browserDefault(request)
  (<function empty at ...>, ())

  >>> resource = None
  >>> resource = dirResource.publishTraverse(request, 'style.css')

  >>> resource
  <falkolab.resource.resourcetypes.FileResource object at ...>

  >>> isinstance(resource.context, resourcetypes.File)
  True

  >>> print resource.GET()
  style data
  >>> print dirResource['style.css'].GET()
  style data

  >>> dirResource['notpresent.css']
  Traceback (most recent call last):
  ...
  KeyError: 'notpresent.css'

  >>> resource = None
  >>> resource = dirResource.publishTraverse(request, 'notpresent.css')
  Traceback (most recent call last):
  ...
  NotFound: ...

  >>> resource = dirResource.publishTraverse(request, 'image.png')
  >>> resource
  <falkolab.resource.resourcetypes.FileResource object at ...>

  >>> isinstance(resource.context, resourcetypes.Image)
  True

  >>> print resource.GET()
  png image data

  >>> subdir = dirResource.publishTraverse(request, 'subfolder')
  >>> subdir
  <falkolab.resource.resourcetypes.DirectoryResource object at ...>

Можно задать допустимые типы ресурсов для директории

  >>> zcml("""
  ... <configure
  ...   xmlns="http://namespaces.falkolab.ru/zope"
  ...   package="falkolab.resource">
  ...
  ...       <resource
  ...           name="resdir2"
  ...           type="directory"
  ...           src="%s">
  ...           <property   name="types" value="image" />
  ...       </resource>
  ...
  ... </configure>
  ... """ %dirName)

  >>> dirResource = None
  >>> dirResource = component.getAdapter(
  ...    request, interface.Interface, name='resdir2')

  >>> dirResource.types
  [u'image']

  >>> resource = dirResource.publishTraverse(request, 'style.css')
  Traceback (most recent call last):
  ...
  NotFound: ...

  >>> resource = dirResource.publishTraverse(request, 'image.png')
  >>> resource
  <falkolab.resource.resourcetypes.FileResource object at ...>

  >>> isinstance(resource.context, resourcetypes.Image)
  True

  >>> os.unlink(os.path.join(dirName, 'script.js'))
  >>> os.unlink(os.path.join(dirName, 'style.css'))
  >>> os.unlink(os.path.join(dirName, 'image.png'))
  >>> os.rmdir(os.path.join(dirName, 'subfolder'))
  >>> os.rmdir(dirName)