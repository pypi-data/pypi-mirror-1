try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from zope.interface import implements

from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.eCards.config import PROJECTNAME
from Products.eCards.interfaces import IECard

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.Marshall import PrimaryFieldMarshaller

schema = ATImageSchema.copy()

schema = schema + Schema((
    TextField('credits',
              languageIndependent=0,
              widget=StringWidget(label='eCard Credits',
                                  label_msgid="label_e-card_credits",
                                  description='Give credit to the photographer of this e-card picture.',
                                  description_msgid="help_e-card_credits",
                                  i18n_domain = "plone")),
    ImageField('thumb',
              required=False,
              languageIndependent=True,
              storage = AnnotationStorage(migrate=True),
              swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
              pil_quality = zconf.pil_config.quality,
              pil_resize_algo = zconf.pil_config.resize_algo,
              max_size = zconf.ATImage.max_image_dimension,
              sizes= {'mini'    : (200, 200),
                      'thumb'   : (128, 128),
                      'tile'    :  (64, 64),
                     },
              widget=ImageWidget(label='Image Thumbnail',
                                 label_msgid="label_e-card_thumbnail",                                 
                                 description='You may choose to upload your own thumbnail of any size to be \
                                    used within the eCard Collection view.  Using image resizing, a 200px, 128px, and \
                                    64px version will be created in addition to your original.  On your eCard Collection, \
                                    you can choose amongst several options for the thumbnail size.  If you do not upload a thumbnail,\
                                    the primary eCard image will be used and again, you can choose amongst several options for the \
                                    thumbnail size when editing your eCard Collection.',
                                 description_msgid="help_e-card_thumbnail XXX autogenerate",                                 
                                 i18n_domain = "plone")),
              ),
    )

finalizeATCTSchema(schema)

class eCard(ATImage):
    """This is the actual eCard image added to the eCard collection 
    """
    implements(IECard)
    
    schema = schema
    meta_type      = 'eCard'
    archetype_name = 'eCard'
    immediate_view = 'image_view'
    default_view   = 'image_view'
    global_allow   = 0
    
    security       = ClassSecurityInfo()
    
    security.declareProtected(permissions.View, 'tag')
    def thumbtag(self, **kwargs):
        """See IECard
        """
        return self.getField('thumb').tag(self, **kwargs)
    
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        
        if name.startswith('thumb'):
            field = self.getField('thumb')
            thumb = None
            if name == 'thumb':
                thumb = field.getScale(self)
            else:
                scalename = name[len('thumb_'):]
                if scalename in field.getAvailableSizes(self):
                    thumb = field.getScale(self, scale=scalename)
            if thumb is not None and not isinstance(thumb, basestring):
                # thumb might be None or '' for empty thumbs
                return thumb

        return ATCTFileContent.__bobo_traverse__(self, REQUEST, name)
    
registerType(eCard, PROJECTNAME)