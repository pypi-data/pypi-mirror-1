# (C) 2005-2009. University of Washington. All rights reserved.

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile \
     import ViewPageTemplateFile

from util import extractInnerView as getView

#Patch for a bug that causes these views not to work
from Products.Five.browser.pagetemplatefile import \
     ZopeTwoPageTemplateFile
        
def _getContext(self):
    while 1:
        self = self.aq_parent
        if not getattr(self, '_is_wrapperish', None):
            return self

class CollageView(BrowserView):
    """Grab the selected view, and stick it into the
    Collage layout.
    """
    __call__ = ViewPageTemplateFile('collage.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

        #Monkey patch for the strange error shown here
        #https://bugs.launchpad.net/zope2/+bug/176566
        ZopeTwoPageTemplateFile._getContext = _getContext

    def getInnerView(self):
        return getView(self.context)
