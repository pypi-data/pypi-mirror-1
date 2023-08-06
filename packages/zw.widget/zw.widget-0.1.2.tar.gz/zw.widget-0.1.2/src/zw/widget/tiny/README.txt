==========
TinyWidget
==========

The widget can render a HTML text input field based on the TinyMCE
JavaScript Content Editor from Moxicode Systems

..http://tinymce.moxiecode.com

  >>> from zope.interface.verify import verifyClass
  >>> from zope.app.form.interfaces import IInputWidget
  >>> from z3c.form.interfaces import IWidget
  >>> from zw.widget.tiny.widget import TinyWidget

The TinyWidget is a widget:

  >>> verifyClass(IWidget, TinyWidget)
   True

The widget can render a textarea field only by adapteing a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = TinyWidget(request)

Such a field provides IWidget:

  >>> IWidget.providedBy(widget)
   True

We also need to register the template for at least the widget and
request:

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import zw.widget.tiny
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(zw.widget.tiny.__file__),
  ...   'tiny_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory, 
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...	  IPageTemplate, name='input')
  
If we render the widget we get the HTML:

  >>> print widget.render()
  <textarea class="tiny-widget" cols="60" rows="10"></textarea>

Adding some more attributes to the widget will make it display more:

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = u'value'
  
  >>> print widget.render()
  <textarea id="id" name="name" class="tiny-widget" cols="60"
            rows="10">value</textarea>

TODO: Testing for ECMAScript code...
