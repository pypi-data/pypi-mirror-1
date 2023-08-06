"""Definition of the Absence content type
"""

from datetime import date

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.interfaces import IAbsence
from plonehrm.absence.config import PROJECTNAME

AbsenceSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.DateTimeField(
        name='startDate',
        widget=atapi.CalendarWidget(
            label=_(u'label_start_date', default=u'Start date'),
            show_hm = False,
        )
    ),

    atapi.DateTimeField(
        name='endDate',
        widget=atapi.CalendarWidget(
            label=_(u'label_end_date', default=u'End date'),
            show_hm = False,
        )
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AbsenceSchema['title'].storage = atapi.AnnotationStorage()
AbsenceSchema['description'].storage = atapi.AnnotationStorage()
AbsenceSchema['description'].widget.visible = {'view': 'visible',
                                               'edit': 'invisible'}
schemata.finalizeATCTSchema(
    AbsenceSchema,
    folderish=True,
    moveDiscussion=False,
    )


class Absence(folder.ATFolder):
    """Absence"""
    implements(IAbsence)

    meta_type = "Absence"
    schema = AbsenceSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    # XXX Make 'text' a rich text field?
    text = atapi.ATFieldProperty('title')
    start_date = atapi.ATDateTimeFieldProperty('startDate')
    end_date = atapi.ATDateTimeFieldProperty('endDate')

    def __repr__(self):
        value = "<Absence: %s" % self.text
        if self.start_date:
            # We get the (python) date instead of the datetime here.
            value += ", " + self.start_date.date().isoformat()
        if self.end_date:
            value += " - " + self.end_date.date().isoformat()
        return value + ">"

    @property
    def days_absent(self):
        """How long did the absence take?

        If the absence has not ended yet, pick the current date as end
        date.
        """
        end_date = self.end_date
        if not end_date:
            end_date = date.today()
        return end_date.toordinal() - self.start_date.toordinal() + 1


    @property
    def is_current_absence(self):
        """ Returns True is the absence is not closed and
        False in the other cases.
        """
        return not bool(self.end_date)

atapi.registerType(Absence, PROJECTNAME)
