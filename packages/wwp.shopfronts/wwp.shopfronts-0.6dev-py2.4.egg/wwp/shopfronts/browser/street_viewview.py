from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.shopfronts import shopfrontsMessageFactory as _

#
from Products.CMFCore.utils import getToolByName

class Istreet_viewView(Interface):
    """
    street_view view interface
    """

    def test():
        """ test method"""


class street_viewView(BrowserView):
    """
    street_view browser view
    """
    implements(Istreet_viewView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
    
    def get_index(self):
        
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        query["type"] = "street_view"
        brains = portal_catalog.searchResults(**query)
        print brains
