# (C) 2005-2009. University of Washington. All rights reserved.

from unittest import TestSuite
from Products.CMFCore.utils import getToolByName

from collective.types.citation.tests.base import CitationTestCase
from collective.types.citation import Citation
from collective.types.citation.content import ICitation

class TestSetupTypes(CitationTestCase):
    """Make sure we can install types, etc.
    """

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')
        #Create a citation test folder
        self.folder.invokeFactory('Folder', id='test_citation')
        self.folder = self.folder.test_citation

    def testSetup(self):
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled('collective.types.citation'),
                        'collective.types.citation installation failed')
        
    def test_types_versioned(self):
        """Make sure the types are versioned.
        I put this here instead of in policy because I want
        the types versioned no matter which policy is used.
        """
        repository = getToolByName(self.portal,
                                   'portal_repository')
        versionable = repository.getVersionableContentTypes()
        self.failUnless('collective.types.Citation' in versionable,
                        'collective.types.Citation is not versionable')

    def test_citation_installed(self):
        self.failUnless('collective.types.Citation' in
                        self.types.objectIds(),
                        'The collective.types.Citation type is not installed')


def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSetupTypes))

    return suite

