from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.portlet.quote import RandomQuoteMessageFactory as _

class IQuote(Interface):
    """Quote"""
    
    # -*- schema definition goes here -*-
    link = schema.TextLine(
        title=_(u"Link"), 
        required=False,
        description=_(u"A link to the quote"),
    )

    source = schema.TextLine(
        title=_(u"Source"), 
        required=True,
        description=_(u"Who said it?"),
    )

