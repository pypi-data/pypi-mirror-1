import unittest
from zope.testing import doctest

from zope import component
from zope import interface
import zope.traversing.adapters
import zope.traversing.namespace
from zope.component import testing
import zope.publisher.interfaces.browser
import z3c.form.testing

import plone.z3cform.macros

def create_eventlog(event=interface.Interface):
    value = []
    @component.adapter(event)
    def log(event):
        value.append(event)
    component.provideHandler(log)
    return value

def setup_defaults():
    # Set up z3c.form defaults
    z3c.form.testing.setupFormDefaults()
    
    # Make traversal work; register both the default traversable
    # adapter and the ++view++ namespace adapter
    component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable, [None])
    component.provideAdapter(
        zope.traversing.namespace.view, (None, None), name='view')

    # Setup ploneform macros
    component.provideAdapter(
        plone.z3cform.macros.Macros,
        (None, None),
        zope.publisher.interfaces.browser.IBrowserView,
        name='ploneform-macros')

def test_suite():
    return unittest.TestSuite([

        doctest.DocFileSuite(
           'crud/README.txt',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocTestSuite(
           'plone.z3cform.crud.crud',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        doctest.DocTestSuite(
           'plone.z3cform.wysiwyg.widget',
           setUp=testing.setUp, tearDown=testing.tearDown,
           ),

        ])
