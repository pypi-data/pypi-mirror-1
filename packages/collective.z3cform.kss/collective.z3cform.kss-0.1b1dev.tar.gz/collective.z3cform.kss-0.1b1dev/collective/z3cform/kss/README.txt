======================
collective.z3cform.kss
======================

First, let's set up KSS debug mode:

    >>> from zope.interface import alsoProvides
    >>> from kss.core.tests.base import IDebugRequest
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.annotation.interfaces import IAttributeAnnotatable

    >>> def make_request(form={}):
    ...     request = TestRequest()
    ...     request.form.update(form)
    ...     alsoProvides(request, IDebugRequest)
    ...     alsoProvides(request, IAttributeAnnotatable)
    ...     return request

Then we create a simple z3c form

    >>> from zope import interface, schema
    >>> from z3c.form import form, field, button
    >>> from plone.z3cform.base import FormWrapper

    >>> class MySchema(interface.Interface):
    ...     age = schema.Int(title=u"Age")

    >>> class MyForm(form.Form):
    ...     fields = field.Fields(MySchema)
    ...     ignoreContext = True # don't use context to get widget data
    ...
    ...     @button.buttonAndHandler(u'Apply')
    ...     def handleApply(self, action):
    ...         data, errors = self.extractData()
    ...         print data['age'] # ... or do stuff

    >>> class MyFormWrapper(FormWrapper):
    ...     form = MyForm
    ...     label = u"Please enter your age"

    >>> from zope.component import provideAdapter
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope.interface import Interface

    >>> provideAdapter(adapts=(Interface, IBrowserRequest),
    ...                provides=Interface,
    ...                factory=MyFormWrapper,
    ...                name=u"test-form")

Let's verify that worked:

    >>> from zope.component import getMultiAdapter
    >>> context = object()
    >>> request = make_request()
    >>> getMultiAdapter((context, request), name=u"test-form")
    <Products.Five.metaclass.MyFormWrapper object ...>

    >>> del context, request

Inline validation
-----------------

Inline validation is invoked via the @@kss_z3cform_inline_validation view.

    >>> from zope.interface import Interface, implements
    >>> class Bar(object):
    ...     implements(Interface)
    >>> context = Bar()
    >>> request = make_request(form={'form.widgets.age': 'Title'})
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")

This is wired up with KSS. When the user leaves a form control with inline
validation enabled, it will be called with the following parameters:

    >>> view.validate_input(formname=u'test-form', fieldname=u'form.widgets.age', value='Title')
    [{'selectorType': 'css', 'params': {'html': u'<![CDATA[The entered value is not a valid integer literal.]]>', 'withKssSetup': u'True'},
      'name': 'replaceInnerHTML',
      'selector': u'#formfield-form-widgets-age div.fieldErrorBox'},
     {'selectorType': 'htmlid',
      'params': {'value': u'error'},
      'name': 'addClass',
      'selector': u'formfield-form-widgets-age'}]

    >>> request = make_request(form={'form.widgets.age': '20'})
    >>> view = getMultiAdapter((context, request), name=u"kss_z3cform_inline_validation")
    >>> view.validate_input(formname=u'test-form', fieldname=u'form.widgets.age', value='20')

