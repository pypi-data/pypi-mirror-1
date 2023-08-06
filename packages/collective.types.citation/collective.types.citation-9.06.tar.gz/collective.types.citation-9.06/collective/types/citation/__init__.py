# (C) 2005-2009. University of Washington. All rights reserved.

#Get the classes and such from the content directory
from collective.types.citation.content import *
from collective.types.citation import config

from Products.Archetypes import atapi
from Products.CMFCore import utils
from zope.i18nmessageid import MessageFactory
CitationMessageFactory = MessageFactory('collective.types.citation')

PROJECTNAME = 'collective.types.citation'

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PROJECTNAME),
        PROJECTNAME)

    for atype, constructor in \
            zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (PROJECTNAME,
                                      atype.portal_type),
                          content_types = (atype,),
                          permission =
            config.ADD_PERMISSIONS[atype.portal_type],
                          extra_constructors = (constructor,),
                          ).initialize(context)
