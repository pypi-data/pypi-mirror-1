"""Definition of the Quote content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from collective.portlet.quote import RandomQuoteMessageFactory as _
from collective.portlet.quote.interfaces import IQuote
from collective.portlet.quote.config import PROJECTNAME

QuoteSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        'quote',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Quote"),
            description=_(u"The quote"),
        ),
        required=True,
    ),

    atapi.StringField(
        'source',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Source"),
            description=_(u"Who said it?"),
        ),
        required=True,
    ),
    
    atapi.StringField(
        'link',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Link"),
            description=_(u"A link to the quote"),
        ),
        validators=('isURL'),
    ),

))

# These make no sense on this content:
QuoteSchema.delField('title')
QuoteSchema.delField('description')

schemata.finalizeATCTSchema(QuoteSchema, moveDiscussion=False)

class Quote(base.ATCTContent):
    """Quote"""
    implements(IQuote)

    meta_type = "Quote"
    schema = QuoteSchema

    # We've remove the title and description fields, but we still need the
    # Title and Description dublin core methods:
    
    def Title(self):
        lines = [x.strip() for x in self.getQuote().splitlines() if x.strip()]
        if not lines:
            firstline = ""
        else:
            firstline = lines[0]
        return self.source + " - " + firstline
    
    #title = property(Title)
        
    def Description(self):
        return ""
    #description = property(Description)
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    quote = atapi.ATFieldProperty('quote')
    link = atapi.ATFieldProperty('link')
    source = atapi.ATFieldProperty('source')


atapi.registerType(Quote, PROJECTNAME)
