"""Definition of the street_view content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from wwp.shopfronts import shopfrontsMessageFactory as _
from wwp.shopfronts.interfaces import Istreet_view
from wwp.shopfronts.config import PROJECTNAME

street_viewSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        'bodytext',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Body Text for Street"),
            description=_(u"Enter the description of the street"),
        ),
    ),


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

street_viewSchema['title'].storage = atapi.AnnotationStorage()
street_viewSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    street_viewSchema,
    folderish=True,
    moveDiscussion=False
)

class street_view(folder.ATFolder):
    """View a street of stores"""
    implements(Istreet_view)

    meta_type = "street_view"
    schema = street_viewSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    bodytext = atapi.ATFieldProperty('bodytext')


atapi.registerType(street_view, PROJECTNAME)
