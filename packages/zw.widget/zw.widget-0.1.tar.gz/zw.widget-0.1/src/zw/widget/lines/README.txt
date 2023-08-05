===========
LinesWidget
===========

The widget can render a HTML text input field, which collects list
items by line.

  >>> from zope.interface.verify import verifyClass
  >>> from zope.app.form.interfaces import IInputWidget
  >>> from z3c.form.interfaces import IWidget
  >>> from zw.widget.lines.widget import LinesWidget

The LinesWidget is a widget:

  >>> verifyClass(IWidget, LinesWidget)
   True

The widget can render a textarea field only by adapteing a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = LinesWidget(request)

Such a field provides IWidget:

  >>> IWidget.providedBy(widget)
   True

We also need to register the template for at least the widget and
request:

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import zw.widget.lines
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(zw.widget.lines.__file__),
  ...   'lines_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory, 
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...	  IPageTemplate, name='input')
  
If we render the widget we get the HTML:

  >>> print widget.render()
  <textarea class="lines-widget"></textarea>

Adding some more attributes to the widget will make it display more:

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = u'value'
  
  >>> print widget.render()
  <textarea id="id" name="name" class="lines-widget">value</textarea>
