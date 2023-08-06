__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import logging
from DateTime import DateTime
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IBaseContent
from Products.plonehrm.interfaces import IEmployeeModule
from plonehrm.absence import config
from plonehrm.absence.interfaces import IEvaluationInterview

from plonehrm.absence import AbsenceMessageFactory as _

logger = logging.getLogger('plonehrm.absence')

schema = atapi.Schema((
    atapi.StringField(
        name='template',
        widget=atapi.SelectionWidget(
            format='select',
            condition='not:object/template_chosen',
            label=_(u'template', default=u'Template'),
            ),
        required=1,
        vocabulary='_templates'
        ),
    atapi.DateTimeField(
        name='date',
        default_method=DateTime,
        widget=atapi.CalendarWidget(
            label=_(u'label_main_date', default=u'Date'),
            )
        ),
    atapi.TextField(
        'text',
        required=False,
        seachable=False,
        primary=True,
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
            description = '',
            label = _(u'label_body_text', default=u'Body Text'),
            rows = 25,
            condition='object/template_chosen'
            ),
        ),
    atapi.LinesField(
        name='improvementAreas',
        widget=atapi.LinesWidget(
            condition='object/template_chosen',
            label=_(u'label_improvementAreas', default=u'Improvement areas'),
            )
        ),
    ))

Interview_schema = atapi.BaseSchema.copy() + schema.copy()

for schema_key in Interview_schema.keys():
    if not Interview_schema[schema_key].schemata == 'default':
        Interview_schema[schema_key].widget.visible={'edit':'invisible',
                                                     'view':'invisible'}


class EvaluationInterview(atapi.BaseContent):
    """
    """
    __implements__ = (atapi.BaseContent.__implements__, )
    implements(IEmployeeModule, IBaseContent, IEvaluationInterview)
    _at_rename_after_creation = True
    schema = Interview_schema

    # plonehrm.absence wants to know what the main date is:
    main_date = atapi.ATDateTimeFieldProperty('date')

    def _templates(self):
        """
        """
        absencetool = getToolByName(self, 'portal_absence', None)
        if absencetool is None:
            return []
        else:
            items = [(item.id, item.Title())
                     for item in absencetool.listTemplates()]
            return atapi.DisplayList(items)

    def template_chosen(self):
        """Determine if the template (a string) has been chosen yet.
        """
        return len(self.template) > 0


atapi.registerType(EvaluationInterview, config.PROJECTNAME)
