# -*- coding: utf-8 -*-
"""
<+ MODULE_NAME +>

Licensed under the <+ LICENSE +> license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: test.py 66971 2008-06-19 17:59:31Z jfroche $
"""

from zope import interface, schema
from z3c.form import form, field, button
from plone.z3cform.base import FormWrapper

class MySchema(interface.Interface):
    age = schema.Int(title=u"Age")

class MyForm(form.Form):
    fields = field.Fields(MySchema)
    ignoreContext = True # don't use context to get widget data
    __name__ = 'test-form'

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        print data['age'] # ... or do stuff

class MyFormWrapper(FormWrapper):
    form = MyForm
    label = u"Please enter your age"


