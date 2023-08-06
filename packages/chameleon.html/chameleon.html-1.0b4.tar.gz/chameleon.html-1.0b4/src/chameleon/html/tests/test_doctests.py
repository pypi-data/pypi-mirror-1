import unittest
import os

import zope.testing
import zope.interface
import zope.component
import zope.component.testing
import zope.configuration.xmlconfig

import chameleon.core.config
import chameleon.core.testing

import chameleon.html
import chameleon.html.tests
import chameleon.html.language


OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

def render_xss(body, content=None, **kwargs):
    if content is not None:
        kwargs[chameleon.core.config.SYMBOLS.slots] = content
    parser = chameleon.html.language.XSSTemplateParser()
    func = chameleon.core.testing.compile_template(
        parser, parser.parse, body, **kwargs)
    return func(**kwargs)

def setUp(suite):
    zope.component.testing.setUp(suite)

def test_suite():
    filesuites = 'language.txt', 'template.txt'
    testsuites = ()
    
    globs = dict(
        render_xss=render_xss,
        interface=zope.interface,
        component=zope.component,
        os=os,
        path=chameleon.html.tests.__path__[0])
    
    chameleon.core.config.DISK_CACHE = False
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocTestSuite(
        "chameleon.html."+dt, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown) \
         for dt in testsuites] + 
        
        [zope.testing.doctest.DocFileSuite(
        dt, optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp, tearDown=zope.component.testing.tearDown,
        package="chameleon.html") for dt in filesuites]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
