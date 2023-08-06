ColorWidget
-----------


The widget can render an input field with color preview::

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form.interfaces import IWidget
  >>> from zw.widget.color.widget import ColorWidget

The ColorWidget is a widget::

  >>> verifyClass(IWidget, ColorWidget)
   True

The widget can render a input field only by adapting a request::

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = ColorWidget(request)

Such a field provides IWidget::

  >>> IWidget.providedBy(widget)
   True

We also need to register the template for at least the widget and
request::

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import zw.widget.color
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(zw.widget.color.__file__),
  ...   'color_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory, 
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...	  IPageTemplate, name='input')
  
If we render the widget we get the HTML::

  >>> print widget.render()
  <input type="text" class="color-widget" value="" />

Adding some more attributes to the widget will make it display more::

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = u'value'
  
  >>> print widget.render()
  <span id="" class="color-widget color-sample"
        style="background-color: #value;">
  </span>
  <input type="text" id="id" name="name" class="color-widget"
         value="value" />

