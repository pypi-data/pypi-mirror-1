# BBB for CMF < 2.1
try:
    from Products.CMFCore.permissions import AddPortalContent
except ImportError:
    from Products.CMFCore.CMFCorePermissions import AddPortalContent

from Products.Archetypes.public import DisplayList

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "LTOnlineTest"
SKINS_DIR = 'skins'

GLOBALS = globals()




