# (C) 2005-2009. University of Washington. All rights reserved. 

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ATFieldProperty
from Products.Archetypes.atapi import IntegerWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.CMFPlone import PloneMessageFactory as _

from zope import schema
from zope.app.container.constraints import contains
from zope.interface import implements
from zope.interface import Interface

class ICitation(Interface):
    """A citation from a journal or website

    Note that only the title and description are required,
    the user may have any mix of additional information.
    """
    title = schema.TextLine(
        title=_(u'Title'),
        required=True)
    description = schema.Text(
        title=_(u'Description'),
        required=True)
    cite_author = schema.TextLine(
        title=_(u'Author(s)'),
        description=_(u'The author or authors of the work being cited'),
        required=False)
    year = schema.TextLine(
        title=_(u'Year'),
        description=_(u'The year that the work being cited was published'),
        required=False)
    location = schema.TextLine(
        title=_(u'Location'),
        description=_(u'Publication Location'),
        required=False)
    fulltext_link = schema.URI(
        title=_(u'Full Text URL'),
        description=_(u'Link to the full text of the work being cited'),
        required=False)
    source = schema.TextLine(
        title=_('Source/Journal/Publisher'),
        description=_('Source/Journal'),
        required=False)
    volume = schema.TextLine(
        title=_(u'Volume'),
        description=_(u'Publication Volume'),
        required=False)
    issue = schema.TextLine(
        title=_(u'Issue'),
        description=_(u'Publication Issue'),
        required=False)
    pages = schema.Int(
        title=_(u'Pages'),
        description=_(u'Number of pages'),
        required=False)
    abstract_link = schema.URI(
        title=_(u'Abstract Link'),
        description=_(u'Link to the abstract of the work'),
        required=False)

CitationSchema = ATContentTypeSchema.copy() + Schema((

    StringField('cite_author',
        widget=StringWidget(label=_(u'Author(s)'),
                                  description=_(u'The author or authors of the work being cited'),
                                  label_msgid='label_author',
                                  i18n_domain='collective.types.citation'),
        required=False,
        searchable=True,
        storage=AnnotationStorage()),

    StringField('year',
        widget=StringWidget(label=_(u'Year'),
                            description=_(u'Publication Year'),
                            label_msgid='label_year',
                            i18n_domain='collective.types.citation'),
        required=False,
        searchable=True,
        storage=AnnotationStorage()),

    StringField('location',
        widget=StringWidget(label=_(u'Publication Location'),
                            description=_(u'Location of the publication office'),
                            label_msgid='label_location',
                            i18n_domain='collective.types.citation'),
        required=False,
        searchable=True,
        storage=AnnotationStorage()),

    StringField('fullTextLink',
        widget = StringWidget(label=_(u'Full Text URL'),
                                 description=_(u'Link to the full text of the work being cited'),
                                 label_msgid='label_full_text_link',
                                 i18n_domain='collective.types.citation'),
        required=False,
        searchable=False,
        storage=AnnotationStorage()),

    StringField('source',
        widget=StringWidget(label=_('Source/Journal'),
                            description=_('Source/Journal'),
                            label_msgid='label_source',
                            i18n_domain='collective.types.citation'),
        required=False,
        searchable=True,
        storage=AnnotationStorage()),

    StringField('volume',
        widget=StringWidget(label=_(u'Volume'),
                              description=_(u'Publication Volume'),
                              label_msgid='label_volume',
                              i18n_domain='collective.types.citation'),
        required=False,
        Searchable=False,
        storage=AnnotationStorage()),

    StringField('issue', 
        widget=StringWidget(label=_(u'Issue'),
                            description=_(u'Publication Issue'),
                            label_msgid='lable_issue',
                            i18n_domain='collective.types.citation'),
        required=False,
        searchable=False,
        storage=AnnotationStorage()),

    StringField('pages', 
        widget=IntegerWidget(label=_(u'Pages'),
                                  description=_(u'Number of pages'),
                                  label_msgid='label_pages',
                                  i18n_domain='collective.types.citation'),
        required=False,
        searchable=False,
        storage=AnnotationStorage()),

    StringField('abstractLink',
        widget=StringWidget(label=_(u'Abstract URL'),
                                     description=_(u'Link to the abstract of the work')),
        required=False,
        searchable=False,
        storage=AnnotationStorage()),
    ))

#Dublin core stuff
CitationSchema['title'].storage = AnnotationStorage()
CitationSchema['title'].widget.label = _(u"Title")
CitationSchema['title'].widget.description = _(u"")

CitationSchema['description'].storage = AnnotationStorage()
CitationSchema['description'].widget.label = _(u"Description")
CitationSchema['description'].widget.description = _("")

class Citation(base.ATCTContent):
    """Citation type for citing journals, publications,
    and links

    Make sure Citation implements ICitation
     >>> from collective.types.citation import ICitation
     >>> from collective.types.citation import Citation
     >>> from zope.interface.verify import verifyObject
     >>> cite = Citation('cite')
     >>> verifyObject(ICitation, cite)
     True
     
    """
    implements(ICitation)
    schema = CitationSchema
    portal_type = meta_type = 'collective.types.Citation'
    _at_rename_after_creation = True

    description = ATFieldProperty('description')
    cite_author = ATFieldProperty('cite_author')
    year = ATFieldProperty('year')
    location = ATFieldProperty('location')
    fulltext_link = ATFieldProperty('fullTextLink')
    source = ATFieldProperty('source')
    volume = ATFieldProperty('volume')
    issue = ATFieldProperty('issue')
    pages = ATFieldProperty('pages')
    abstract_link = ATFieldProperty('abstractLink')


base.registerATCT(Citation, 'collective.types.citation')
