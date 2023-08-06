try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.CMFCore import permissions
from Products.eCards.config import PROJECTNAME
from Products.eCards.interfaces import IECardCollection

from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

# XXX needed?
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.ATContentTypes.interfaces import IATFolder

schema = ATFolderSchema.copy()

eCardCollectionSchema = schema + Schema((
    TextField('text',
        required = False,
        searchable = True,
        primary = True,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATNewsItem.allowed_content_types,
        widget = RichWidget(
            description = "",
            description_msgid = "help_body_text",
            label = "Body Text",
            label_msgid = "label_body_text",
            rows = 25,
            i18n_domain = "plone",
            allow_file_upload = zconf.ATDocument.allow_document_upload)
        ),
    IntegerField('eCardsPerRow',
              languageIndependent=1,
              default=5,
              validators=('isInt',),
              widget=IntegerWidget(label='Number of eCard thumbnails per row',
                                label_msgid="label_ecardsPerRow_description",
                                description="""The default eCard Collection template outputs eCards \
                                    as thumbnails with the dimension of 128px by 128px in rows.  Depending \
                                    upon the width of the site's graphic design and the desired thumbnail size \
                                    , more or fewer per row will look appropriate.  Set the number of eCards per \
                                    row your graphic design can accommodate.""",
                                description_msgid="help_ecardsPerRow_description",
                                i18n_domain = "plone",)),
    StringField('thumbSize',
              languageIndependent=1,
              default='thumb',
              vocabulary=DisplayList((('original','Original size'),('mini','Mini (200px x 200px)'),\
                    ('thumb','Thumb (128px x 128px)'),('tile','Tile (64px x 64px)'),)),
              widget=SelectionWidget(label='Thumbnail Size (in pixels)',
                                format="select",
                                label_msgid="label_thumbSize_description",
                                description="""Override the default dimensions (128px x 128px) for your eCard thumbnails.  \
                                If you choose original, you should plan on creating a custom thumbnail for each of your eCard images.""",
                                description_msgid="help_thumbSize_description",
                                i18n_domain = "plone",)),
    TextField('emailSubject',
              languageIndependent=0,
              schemata='email',
              widget=StringWidget(label='Email Subject',
                                  label_msgid="label_email_subject",
                                  description="""This is the subject of the email sent to eCard \
                                               recipient.  This subject will be prepended with \
                                               sender's first name (i.e. a value like "has sent you an \
                                               eCard from example.com!" would result in "John has sent you an \
                                               eCard from example.com!").""",
                                  description_msgid="help_email_subject",
                                  i18n_domain = "plone",)),
    TextField('emailAppendedMessage',
              languageIndependent=0,
              schemata='email',
              default_content_type = zconf.ATNewsItem.default_content_type,
              default_output_type = 'text/x-html-safe',
              allowable_content_types = zconf.ATNewsItem.allowed_content_types,
              widget=RichWidget(label='Email Appended Message',
                                label_msgid="label_email_call_to_action",
                                description="""A default caption or message for all eCards within the collection \
                                    appearing below the eCard sender's custom message.  This is used \
                                    to encourage a relationship between the organization and the potential constituents \
                                    and/or customers receiving each eCard.""",
                                description_msgid="help_email_call_to_action",
                                i18n_domain = "plone",)),
    ),
)

finalizeATCTSchema(eCardCollectionSchema)

class eCardCollection(ATFolder):
    """eCard Collection is a folderish object that allows the addition of sortable eCards
    """
    implements(IECardCollection)
    
    schema = eCardCollectionSchema
    content_icon="ecardcollection_icon.gif"
    filter_content_types = 1
    allowed_content_types = ['eCard',]
    
    meta_type      = 'ECardCollection'
    archetype_name = 'eCard Collection'
    immediate_view = 'ecardcollection_view'
    default_view   = 'ecardcollection_view'
    _at_rename_after_creation = True
    
    security       = ClassSecurityInfo()
    
registerType(eCardCollection, PROJECTNAME)
