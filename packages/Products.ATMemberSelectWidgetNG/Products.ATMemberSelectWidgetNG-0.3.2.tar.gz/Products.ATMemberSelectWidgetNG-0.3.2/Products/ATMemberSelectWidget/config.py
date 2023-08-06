# just to be compatible with the general AT approach

PROJECTNAME = "ATMemberSelectWidget"
SKINS_DIR = 'skins'
GLOBALS = globals()

try:
    from Products.CMFCore.permissions import AddPortalContent
except ImportError:
    from Products.CMFCore.CMFCorePermissions import AddPortalContent

ADD_CONTENT_PERMISSION = AddPortalContent
