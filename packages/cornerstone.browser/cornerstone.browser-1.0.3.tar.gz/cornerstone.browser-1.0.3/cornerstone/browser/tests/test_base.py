#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

import unittest

import zope.app.component
import zope.app.publisher

import Products.Five

from pprint import pprint

#from zope.testing.doctestunit import DocFileSuite

from interact import interact

#import cornerstone.browser

from zope.testing import doctest
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '../base.txt',
]

def test_suite():
    setUp()
    XMLConfig('meta.zcml', zope.app.component)()
    #XMLConfig('meta.zcml', Products.Five)()
    #XMLConfig('configure.zcml', cornerstone.browser)()
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file, 
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint},
        ) for file in TESTFILES
    ])
    tearDown()

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite') 

