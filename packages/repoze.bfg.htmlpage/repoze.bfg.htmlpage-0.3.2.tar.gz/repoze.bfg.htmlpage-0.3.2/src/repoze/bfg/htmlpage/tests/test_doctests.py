import os

import zope.interface
import zope.component
import zope.testing

import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing

import repoze.bfg.htmlpage
import repoze.bfg.htmlpage.tests

def setUp(suite):
    zope.component.testing.setUp(suite)

def test_suite():
    doctests = "zcml.txt", "template.txt",
    
    globs = dict(interface=zope.interface,
                 component=zope.component,
                 path=repoze.bfg.htmlpage.tests.__path__[0],
                 os=os)

    return unittest.TestSuite(
        [zope.testing.doctest.DocFileSuite(
                doctest,
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                globs=globs,
                tearDown=zope.component.testing.tearDown,
                package="repoze.bfg.htmlpage") for doctest in doctests]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
