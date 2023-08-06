================================================================================
falkolab.extjslayer components
================================================================================

  >>> from zope import component, interface
  >>> from falkolab.resource.interfaces import IExtensibleResourceFactory,IResourcePropertyManager
  >>> from falkolab.extjslayer.interfaces import IExtJSLayer
  >>> class FooFactory(object):
  ...    interface.implements(IExtensibleResourceFactory)
  
  >>> test = FooFactory()
  >>> a = component.getAdapter(test,IResourcePropertyManager)
  >>> a
  <falkolab.resource.adapters.DefaultResourceTypePropertyAdapter object at ...>
  
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> interface.directlyProvides(request,IExtJSLayer)
  >>> response = request.response
  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='fl-ext-base-adapter')

  >>> resource
  <falkolab.resource.resourcetypes.FileResource object at ...>
  
  >>> resource()
  u'http://127.0.0.1/@@/fl-ext-base-adapter'
  
  >>> resource.GET()
  '...Ext JS Library...'
    
  >>> resource = component.getAdapter(
  ...    request, interface.Interface, name='fl-ext-all.css')
  
  >>> resource
  <falkolab.resource.zrt.zrtresourcetype.ZRTResource object at ...>
  
  >>> resource()
  u'http://127.0.0.1/@@/fl-ext-all.css'
  
  >>> resource.GET()
  u'...@@/fl-ext-resources/images...'