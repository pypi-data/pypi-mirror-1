__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Products.Archetypes import atapi
from Products.CMFCore.utils import ImmutableId
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

import config

absenceevaluation_schema = atapi.BaseFolderSchema.copy()


class AbsenceTool(ImmutableId, atapi.BaseFolder):
    """ Absence Tool, stores EvaluationInterview templates.
    """
    security = ClassSecurityInfo()
    __implements__ = (atapi.BaseFolder.__implements__, )

    id = 'portal_absence'
    typeDescription = "Absence evaluations templates"
    typeDescMsgId = 'description_edit_absencetool'
    schema = absenceevaluation_schema

    def __init__(self, *args, **kwargs):
        self.setTitle('Absence Evaluations Templates')

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        pass

    security.declareProtected(ModifyPortalContent, 'reindexObjectSecurity')
    def reindexObjectSecurity(self, skip_self=False):
        pass

    def listTemplates(self, type='absence_evaluation'):
        """List the templates in this tool.

        Optionally list the templates from a higher level
        portal_contracts tool as well.  This is done by trying to call
        getUseHigherLevelTemplates on the current tool.  This method
        is not available by default, but can be implemented by third
        party products.  Default is False.  If you always want this to
        be True, add a python script getUseHigherLevelTool in the
        portal_skins/custom folder that just returns True.

        We return full objects; returning just ids will fail as we
        then have no way of knowing in which portal_contracts that
        template id is.
        """
        templates = self.contentValues()

        try:
            recursive = self.getUseHigherLevelTool()
        except AttributeError:
            recursive = False

        if recursive:
            # Get our grand parent and ask him for a portal_contracts
            # tool.  Note that if we ask our parent, then a
            # getToolByName will return ourselves, which is not what
            # we want.
            grand_parent = aq_parent(aq_parent(aq_inner(self)))
            higher_tool = getToolByName(grand_parent, self.id, None)
            if higher_tool is not None:
                templates += higher_tool.listTemplates()

        # We now filter the template to keep only Template object
        # for which the type is the one asked.
        filtered = []

        for template in templates:
            try:
                if template.getType() == type:
                    filtered.append(template)
            except:
                # Old templates are left in the folder.
                pass

        return filtered


atapi.registerType(AbsenceTool, config.PROJECTNAME)
