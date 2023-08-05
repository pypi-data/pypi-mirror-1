#!/usr/local/env/python
#############################################################################
# Name:         tests.py
# Purpose:      
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import unittest
import zope
import sys
from zope.testing import doctest, doctestunit

import zope.component.testing
from zope.testing import module

from bebop.protocol.protocol import adapterProtocol
from bebop.protocol.browser import pageProtocol

def setUpReadMe(test):
    adapterProtocol.deactivate()
    module.setUp(test, 'bebop.protocol.readme')

def tearDownReadMe(test):
    module.tearDown(test, 'bebop.protocol.readme')
 
def setUpGeneric(test):
    module.setUp(test, 'bebop.protocol.generic_txt')

def tearDownGeneric(test):
    module.tearDown(test, 'bebop.protocol.generic_txt')


def setUpBrowser(test):
    module.setUp(test, 'bebop.protocol.browser_txt')

def tearDownBrowser(test):
    module.tearDown(test, 'bebop.protocol.browser_txt')
    pageProtocol.reopen()


def test_suite():

    return unittest.TestSuite((

        doctest.DocFileSuite("README.txt", 
                    setUp=setUpReadMe, 
                    tearDown=tearDownReadMe,
                    globs={'pprint': doctestunit.pprint,
                            'zope': zope},
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),
                    
        doctest.DocFileSuite("browser.txt", 
                    setUp=setUpBrowser, 
                    tearDown=tearDownBrowser,
                    globs={'pprint': doctestunit.pprint,
                            'zope': zope},
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),        

        doctest.DocFileSuite("generic.txt", 
                    setUp=setUpGeneric, 
                    tearDown=tearDownGeneric,
                    globs={'pprint': doctestunit.pprint,
                            'zope': zope},
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),        

        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')    
