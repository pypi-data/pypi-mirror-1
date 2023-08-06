from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.eCards.config import PROJECTNAME, GLOBALS, \
    DEFAULT_ADD_CONTENT_PERMISSION, SKINS_DIR

from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('eCards')

registerDirectory(SKINS_DIR + '/ecards_images', GLOBALS)
registerDirectory(SKINS_DIR + '/ecards_templates', GLOBALS)
registerDirectory(SKINS_DIR + '/ecards_styles', GLOBALS)

def initialize(context):
    
    import content
    
    ##########
    # Add our content types
    #
    # This approach borrowed from ATContentTypes
    #
    listOfTypes = listTypes(PROJECTNAME)
    
    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)
    
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        
        permission = DEFAULT_ADD_CONTENT_PERMISSION
        
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permission,
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)
