# (C) 2005-2009. University of Washington. All rights reserved.

from unittest import TestSuite

from collective.types.citation.tests.base import CitationTestCase
from collective.types.citation.tests.base import Session
from collective.types.citation import Citation
from collective.types.citation.content import ICitation

class TestViews(CitationTestCase):
    """Make sure the different views work properly
    """
    def afterSetUp(self):
        self.folder.invokeFactory('collective.types.Citation',
                                  id=u'cite2')

        cite = self.folder.cite2
        cite.setTitle('Citation Title')
        cite.setCite_author('Author')
        cite.setLocation('Location')
        cite.setFullTextLink('http://test.com')
        cite.setSource('Source')
        cite.setVolume('Volume')
        cite.setIssue('Issue')
        cite.setPages('4')
        cite.setAbstractLink('http://Abstract.com')
        cite.REQUEST.SESSION = Session()
        cite.REQUEST.SESSION.id = '123'

    def testChangeLayout(self):
        """Make sure all layouts can be switched to
        """
        cite = self.folder.cite2

        for layout in ('article_page', 'book_page',
                       'report_page', 'other_page'):
            cite.setLayout(layout)
            self.assertEquals(cite.getLayout(),
                              layout,
                              'Layout could not be '\
                              'changed to %s' % layout)
        
    def testLayouts(self):
        """Make sure the layouts don't throw any errors
        """
        cite = self.folder.cite2

        for layout in ('article', 'article_page',
                       'book', 'book_page',
                       'report', 'report_page',
                       'other', 'other_page'):
            found = cite.restrictedTraverse(layout)()
            #self.failUnless('http://example.com' in
            #                found,
            #                '%s layout was not '\
            #                'outputted properly.\n'\
            #                'Found:\n%s' % (layout, found))


class TestCreateCitation(CitationTestCase):
    """Make sure we can create Citations
    """

    def testCreateCitation(self):
        self.folder.invokeFactory('collective.types.Citation',
                                  id='cite1')
        cite = self.folder.cite1
        self.assertEquals('cite1', cite.id,
                          "Citation id should be 'cite1' "\
                          ", instead it's %s" % \
                          cite.id)
        self.assertEquals(cite.default_view, 'base_view',
                          'default_view should be base_view')

def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestCreateCitation))
    suite.addTest(makeSuite(TestViews))

    return suite

