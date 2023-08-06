from z3c.form import form, subform, interfaces

import plone.z3cform
import os

path = os.path.join(os.path.dirname(plone.z3cform.__file__), "subform.pt")
factory = form.FormTemplateFactory(path, form=interfaces.ISubForm)
