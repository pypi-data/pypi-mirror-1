import zope.interface
import zope.component

import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing
import zope.configuration.xmlconfig

import repoze.bfg.httprequest

def setUp(suite):
    zope.component.testing.setUp(suite)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', repoze.bfg.httprequest)()
    
def test_suite():
    doctests = 'README.txt',
    
    globs = dict(
        interface=zope.interface,
        component=zope.component)
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
        filename,
        optionflags=OPTIONFLAGS,
        setUp=setUp,
        globs=globs,
        tearDown=zope.component.testing.tearDown,
        package="repoze.bfg.httprequest") for filename in doctests])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
