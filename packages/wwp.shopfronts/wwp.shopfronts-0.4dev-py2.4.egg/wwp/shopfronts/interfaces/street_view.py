from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.shopfronts import shopfrontsMessageFactory as _

class Istreet_view(Interface):
    """View a street of stores"""
    
    # -*- schema definition goes here -*-
    bodytext = schema.SourceText(
        title=_(u"Body Text for Street"), 
        required=False,
        description=_(u"Enter the description of the street"),
    )

