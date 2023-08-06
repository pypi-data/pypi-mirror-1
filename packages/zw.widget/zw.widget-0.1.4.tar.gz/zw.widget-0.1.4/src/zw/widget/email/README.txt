
EmailWidget
-----------


The widget can render an ordinary input field::

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form.interfaces import IWidget, INPUT_MODE, DISPLAY_MODE
  >>> from zw.widget.email.widget import EmailWidget

The EmailWidget is a widget::

  >>> verifyClass(IWidget, EmailWidget)
   True

The widget can render a input field only by adapting a request::

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = EmailWidget(request)

Such a field provides IWidget::

  >>> IWidget.providedBy(widget)
   True

We also need to register the template for at least the widget and
request::

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import zw.widget.email
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(zw.widget.email.__file__),
  ...   'email_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory, 
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...	  IPageTemplate, name='input')
  
If we render the widget we get the HTML::

  >>> print widget.render()
  <input type="text" class="email-widget" value="" />

Adding some more attributes to the widget will make it display more::

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = u'name@domain.tld'
  
  >>> print widget.render()
  <input type="text" id="id" name="name" class="email-widget"
         value="name@domain.tld" />

More interesting is to the display view::

  >>> widget.mode = DISPLAY_MODE
  >>> template = os.path.join(os.path.dirname(zw.widget.email.__file__),
  ...                         'email_display.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='display')
  >>> print widget.render()
  <span id="id" class="email-widget">
    <a href="mailto:name@domain.tld">
      name@domain.tld
    </a>
  </span>
      
But if we are not authenticated it should be obscured:

  >>> widget.obscured = True
  >>> print widget.render()
  <span id="id" class="email-widget">
      name@domain.tld
  </span>

