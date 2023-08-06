## The Project Name
PROJECTNAME = "eCards"

## Globals variable
GLOBALS = globals()

## Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

## The skins dir
SKINS_DIR = 'skins'

## Archetype content objects associated with product
ALLTYPES = ('eCard', 'eCardCollection',)

## Skin directories associated with product
ALLSKINS = ('ecards_images', 'ecards_templates', 'ecards_styles')

## Addition permissions added to the eCards namespace
# XXX There has to be something I'm missing here
from Products.CMFCore import permissions as CMFCorePermissions
SendECard = "eCards: Send eCard"
CMFCorePermissions.setDefaultRoles(SendECard, ['Manager','Anonymous']) 

