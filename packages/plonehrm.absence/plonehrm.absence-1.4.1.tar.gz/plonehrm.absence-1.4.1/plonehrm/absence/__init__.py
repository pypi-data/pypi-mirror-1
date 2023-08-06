from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore import utils as cmfutils
import config
from Products.CMFPlone.utils import ToolInit

import tool
from tool import AbsenceTool

from zope.i18nmessageid import MessageFactory
AbsenceMessageFactory = MessageFactory(u'absence')


def initialize(context):
    # imports packages and types for registration
    import content
    content # PYFLAKES

    permissions = dict(Absence='plonehrm: Add absence',
                       Note='plonehrm: Add note',
                       AbsenceFile='plonehrm: Add absence file',
                       AbsenceTool='plonehrm: Add absence tool',
                       EvaluationInterview='plonehrm: Add evaluation interview')

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME, atype.archetype_name)
        cmfutils.ContentInit(
            kind,
            content_types = (atype, ),
            permission = permissions[atype.portal_type],
            extra_constructors = (constructor, ),
            ).initialize(context)

    # Initialize portal tools
    tools = [tool.AbsenceTool]
    ToolInit(config.PROJECTNAME +' Tools',
             tools = tools,
             icon='tool.gif'
             ).initialize( context )
