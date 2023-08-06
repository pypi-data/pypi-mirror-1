import unittest

import plone.portlets

import zope.component
import zope.security
import zope.app.security
import zope.app.component
import zope.app.pagetemplate

import zope.app.event
import zope.app.container
import zope.contentprovider

from zope.testing import doctest
from zope.component.testing import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS


def configurationSetUp(test):
    setUp()
    
    XMLConfig('meta.zcml', zope.security)()
    XMLConfig('meta.zcml', zope.app.security)()
    XMLConfig('meta.zcml', zope.app.component)()
    XMLConfig('meta.zcml', zope.app.pagetemplate)()

    # BBB conditional code for loading the utility dispatchers
    # In Zope 2.11 they are in zope.component
    try:
        XMLConfig('configure.zcml', zope.component)()
    except IOError:
        pass
    # In Zope 2.10 they are in zope.app.event
    try:
        XMLConfig('configure.zcml', zope.app.event)()
    except IOError:
        pass

    XMLConfig('configure.zcml', zope.app.security)()
    XMLConfig('configure.zcml', zope.app.container)()
    XMLConfig('configure.zcml', zope.contentprovider)()
    XMLConfig('configure.zcml', plone.portlets)()


def configurationTearDown(test):
    tearDown()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=configurationSetUp,
            tearDown=configurationTearDown,
            optionflags=optionflags),
    ), )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
