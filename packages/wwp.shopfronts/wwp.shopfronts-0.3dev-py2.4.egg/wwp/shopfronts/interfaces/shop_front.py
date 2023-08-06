from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.shopfronts import shopfrontsMessageFactory as _

class Ishop_front(Interface):
    """Online shopfronts for stores"""
    
    # -*- schema definition goes here -*-
    rssfeed = schema.TextLine(
        title=_(u"Feed to post"), 
        required=False,
        description=_(u"RSS/news feed from twitter, blog, facebook, etc"),
    )

    shopphone = schema.TextLine(
        title=_(u"Telephone"), 
        required=False,
        description=_(u"enter telephone number"),
    )

    shopwebsite = schema.TextLine(
        title=_(u"Website"), 
        required=False,
        description=_(u"htt://...."),
    )

    shopaddress = schema.Text(
        title=_(u"Address"), 
        required=False,
        description=_(u"enter store address"),
    )

    store_logo = schema.Bytes(
        title=_(u"Store logo"), 
        required=True,
        description=_(u"Upload a logo for the store"),
    )

    store_image = schema.Bytes(
        title=_(u"Store Image"), 
        required=True,
        description=_(u"Upload an image of the store"),
    )

    special_notices = schema.Text(
        title=_(u"Special Notices"), 
        required=True,
        description=_(u"Enter details of special offers, or notices"),
    )

    opening_times = schema.Text(
        title=_(u"Store opening times"), 
        required=True,
        description=_(u"enter the daily opening times of the store"),
    )

    long_desc = schema.SourceText(
        title=_(u"Detailed store info"), 
        required=True,
        description=_(u"Enter the detailed store information"),
    )

