from zope.i18nmessageid import MessageFactory

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils as ut

from config import *

PingToolMessageFactory = MessageFactory(PROJECTNAME)

def initialize(context):
    import PingInfo, PingTool
    ut.ToolInit("PingTool", (PingTool.PingTool, ), icon=TOOL_ICON,
                  ).initialize(context)

    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)

    ut.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
