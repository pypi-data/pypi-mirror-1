"""Definition of the shop_front content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from wwp.shopfronts import shopfrontsMessageFactory as _
from wwp.shopfronts.interfaces import Ishop_front
from wwp.shopfronts.config import PROJECTNAME

shop_frontSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-



    atapi.TextField(
        'shopaddress',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Address"),
            description=_(u"enter store address"),
        ),
    ),

    atapi.StringField(
        'shopphone',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Telephone"),
            description=_(u"enter telephone number"),
        ),
    ),
   
    atapi.StringField(
        'shopwebsite',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Website"),
            description=_(u"htt://...."),
        ),
    ),
    

    atapi.TextField(
        'special_notices',
        default_content_type = 'text/restructured',
        default_output_type = 'text/x-html-safe',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Special Notices"),
            description=_(u"Enter details of special offers, or notices"),
        ),
    ),

    atapi.TextField(
        'opening_times',
        default_content_type = 'text/restructured',
        default_output_type = 'text/x-html-safe',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Store opening times"),
            description=_(u"enter the daily opening times of the store"),
        ),
    ),

    atapi.TextField(
        'long_desc',
        default_content_type = 'text/restructured',
        default_output_type = 'text/x-html-safe',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Detailed store info"),
            description=_(u"Enter the detailed store information"),
        ),
    ),
    
    atapi.StringField(
        'rssfeed',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Feed to post"),
            description=_(u"RSS/news feed from twitter, blog, facebook, etc"),
        ),
    ),

    atapi.ImageField(
        'store_logo',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Store logo"),
            description=_(u"Upload a logo for the store"),
        ),
        validators=('isNonEmptyFile'),
        original_size = (300,300),
        sizes = {'mini'    : (200, 200),
                 'thumb'   : (128, 128),
                 'icon'    : (32,  32),
                },
    ),

    atapi.ImageField(
        'store_image',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Store Image"),
            description=_(u"Upload an image of the store"),
            
        ),
        original_size = (500,500),
        validators=('isNonEmptyFile'),
        sizes = {'front'   : (300, 200),
                 'thumb'   : (128, 128),
                 'icon'    : (32,  32),
                 },
    ),



    


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

shop_frontSchema['title'].storage = atapi.AnnotationStorage()
shop_frontSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(shop_frontSchema, moveDiscussion=False)

class shop_front(base.ATCTContent):
    """Online shopfronts for stores"""
    implements(Ishop_front)

    meta_type = "shop_front"
    schema = shop_frontSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    rssfeed = atapi.ATFieldProperty('rssfeed')

    shopphone = atapi.ATFieldProperty('shopphone')

    shopwebsite = atapi.ATFieldProperty('shopwebsite')

    shopaddress = atapi.ATFieldProperty('shopaddress')

    store_logo = atapi.ATFieldProperty('store_logo')

    store_image = atapi.ATFieldProperty('store_image')

    special_notices = atapi.ATFieldProperty('special_notices')

    opening_times = atapi.ATFieldProperty('opening_times')

    long_desc = atapi.ATFieldProperty('long_desc')
    
    
        # workaround to make resized images
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('store_image'):
            field = self.getField('store_image')
            image = None
            if name == 'store_image':
                image = field.getScale(self)
            else:
                scalename = name[len('store_image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        if name.startswith('store_logo'):
            field = self.getField('store_logo')
            image = None
            if name == 'store_logo':
                image = field.getScale(self)
            else:
                scalename = name[len('store_logo_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        return base.ATCTContent.__bobo_traverse__(self, REQUEST, name)
    
    @property
    def is_published(self):        
        #app = context.restrictedTraverse(r.getPath()) # chechout the object
        #check the permission of the object for anonymous user:
        obj_viewed = [x for x in self.permissionsOfRole('Anonymous') if x['name']=='View']
        if obj_viewed[0]['selected'] == 'SELECTED':
            return True
        else:
            return False


atapi.registerType(shop_front, PROJECTNAME)
