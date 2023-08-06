# (C) 2005-2009. University of Washington. All rights reserved. 

from doctest import ELLIPSIS
from doctest import NORMALIZE_WHITESPACE
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from collective.types.citation.tests.base import CitationFunctionalTestCase

#Doctests relative to the main project directory
#(must contain file extension)
list_doctests = ['content.py',
                 'tests/citation.txt',]

def test_suite():
    return unittest.TestSuite(
        [Suite(filename,
               optionflags=(NORMALIZE_WHITESPACE | ELLIPSIS),
               package='collective.types.citation',
               test_class=CitationFunctionalTestCase)
         for filename in list_doctests]
        )
