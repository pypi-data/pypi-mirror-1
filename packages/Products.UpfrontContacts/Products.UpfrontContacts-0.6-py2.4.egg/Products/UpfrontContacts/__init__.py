from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

import schemapatch

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    import CustomFields
    import ContactManager
    import Organisation
    import Person

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    from UpfrontContactsTool import UpfrontContactsTool

    ToolInit(
        PROJECTNAME + ' Tools',
        tools = (UpfrontContactsTool,),
        product_name = PROJECTNAME,
        icon='tool.gif'
        ).initialize(context)
