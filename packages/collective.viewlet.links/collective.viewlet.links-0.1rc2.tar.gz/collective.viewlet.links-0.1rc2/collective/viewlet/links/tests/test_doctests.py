import doctest
from zope.testing.doctest import DocTestSuite
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from collective.viewlet.links.config import PROJECTNAME
from collective.viewlet.links.tests.base import FunctionalTestCase

#Doctests relative to the main project directory
#(must contain file extension)
list_doctests = [
    'README.txt']
OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS


doctestModules = ['collective.viewlet.links.annotations',
                  ]

doctests= []
for module in doctestModules:
    doctests.append(DocTestSuite(module,
                                 optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,)
                                 )

def test_suite():
    return unittest.TestSuite(
        doctests +

        [Suite(filename,
               optionflags=OPTIONFLAGS,
               package=PROJECTNAME,
               test_class=FunctionalTestCase)
         for filename in list_doctests])
