# (C) 2005-2009. University of Washington. All rights reserved.

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile \
     import ViewPageTemplateFile
#from plone.memoize.instance import memoize
from collective.types.citation.content import ICitation

#Patch for a bug that causes these views not to work
from Products.Five.browser.pagetemplatefile import \
     ZopeTwoPageTemplateFile
        
def _getContext(self):
    while 1:
        self = self.aq_parent
        if not getattr(self, '_is_wrapperish', None):
            return self

class CitationView(BrowserView):
    """Parent Citation View
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

        #Monkey patch for the strange error shown here
        #https://bugs.launchpad.net/zope2/+bug/176566
        ZopeTwoPageTemplateFile._getContext = _getContext

class CitationPageView(CitationView):
    """Article view mode for a Citation
    """
    template = 'citation_page.pt'
    __call__ = ViewPageTemplateFile(template)

    def getLayout(self):
        selected = self.context.getLayout()
        view_name = selected[:-5]
        view = ''.join(('@@', view_name))
        return self.context.restrictedTraverse(view)()

class ArticleView(CitationView):
    """Article view mode for a Citation
    """
    template = 'citation_article.pt'
    __call__ = ViewPageTemplateFile(template)

class BookView(CitationView):
    """Book view mode for a Citation
    """
    __call__ = ViewPageTemplateFile('citation_book.pt')

class ReportView(CitationView):
    """Report view mode for a Citation
    """
    __call__ = ViewPageTemplateFile('citation_report.pt')

class OtherView(CitationView):
    """Default view mode for a Citation
    """
    __call__ = ViewPageTemplateFile('citation_other.pt')
