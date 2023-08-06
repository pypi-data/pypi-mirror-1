import zope.interface
import zope.component
import zope.testing

import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing
import zope.configuration.xmlconfig

import chameleon.zpt
import vudo.cmf

def setUp(suite):
    zope.component.testing.setUp(suite)
    zope.configuration.xmlconfig.XMLConfig(
        'configure.zcml', chameleon.zpt)()
    zope.configuration.xmlconfig.XMLConfig(
        'configure.zcml', vudo.cmf)()
    
def test_suite():
    doctests = "manager.txt",
    
    globs = dict(
        interface=zope.interface,
        component=zope.component)
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocFileSuite(
                doctest,
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                globs=globs,
                tearDown=zope.component.testing.tearDown,
                package="vudo.cmf") for doctest in doctests]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
