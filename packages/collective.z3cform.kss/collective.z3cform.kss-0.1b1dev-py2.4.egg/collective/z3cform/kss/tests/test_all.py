# -*- coding: utf-8 -*-
"""
collective.z3cform.kss

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: test_all.py 66966 2008-06-19 16:22:57Z jfroche $
"""

import unittest
from zope.testing import doctest, cleanup
from Products.Five import zcml

import Products.Five
import kss.core
import kss.core.tests
import plone.app.kss
import plone.app.form
import collective.z3cform.kss
import z3c.form

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE)


def setUp(test):
    zcml.load_config('configure.zcml', Products.Five)
    zcml.load_config('meta.zcml', kss.core)
    zcml.load_config('configure.zcml', kss.core)
    zcml.load_config('configure-unittest.zcml', kss.core.tests)
    zcml.load_config('configure.zcml', plone.app.form)
    zcml.load_config('configure.zcml', plone.app.kss)
    zcml.load_config('meta.zcml', z3c.form)
    zcml.load_config('configure.zcml', z3c.form)
    zcml.load_config('configure.zcml', collective.z3cform.kss)

def tearDown(test):
    cleanup.cleanUp()

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('README.txt',
                             package='collective.z3cform.kss',
                             setUp=setUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
