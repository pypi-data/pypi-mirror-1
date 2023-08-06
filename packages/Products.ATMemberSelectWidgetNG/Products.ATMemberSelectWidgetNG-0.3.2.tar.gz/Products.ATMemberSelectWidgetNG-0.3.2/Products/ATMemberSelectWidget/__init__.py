from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import process_types, listTypes
from config import *

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    import ATMemberSelectDemo

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
