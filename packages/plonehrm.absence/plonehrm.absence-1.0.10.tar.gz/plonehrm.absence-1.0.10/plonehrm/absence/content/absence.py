"""Definition of the Absence content type
"""

from datetime import date
from Acquisition import aq_chain
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.interfaces import IAbsence
from Products.plonehrm.interfaces import IEmployee
from plonehrm.absence.config import PROJECTNAME
from zope import component

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

    atapi.IntegerField(
        name='absence_length',
        widget=atapi.IntegerWidget(
            label=_(u'label_days_absent', default=u'Absence length (days)'),
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

    def get_employee(self):
        """Get the employee that this contract is in.

        Note that we probably are in the portal_factory, so our direct
        parent is not an Employee.  But we can traverse up the
        acquisition chain to find it.
        """
        for parent in aq_chain(self):
            if IEmployee.providedBy(parent):
                return parent

    def days_absent(self):
        """How long did the absence take?

        If the absence has ended, return the length stored on the
        object. Else try to estimate the number of days someone hasn't
        worked.

        Note 1: if the start date of the absence is in the future,
        return 1.

        Note 2: due to the way the algorithm works, should the
        employee works a 0 hour/day contract the employee will get 0
        sick days by his/her name when they are sick or were sick.
        """

        if self.end_date:
            return self.get('absence_length', 0)

        end_date = date.today()
        if end_date.toordinal() < self.start_date.toordinal():
            # Apparently the absence starts in the future. Since
            # (currently) absences can only be started one day in the
            # future, we'll count this case as the employee being sick
            # a single day.  the employee is absent for a day.
            return 1

        parent = self.get_employee()
        if parent is None:
            return
        view = component.getMultiAdapter((parent, self.REQUEST),
                                         name=u'contracts')
        current = view.current_contract()
        if current is not None:
            days_per_week = current.getDaysPerWeek()
        else:
            days_per_week = 5

        absence_length = float(end_date.toordinal() -
                               self.start_date.toordinal() + 1)
        sickness_days = (days_per_week / 7.0) * absence_length
        rounded_sickness = int(round(sickness_days))
        return rounded_sickness

    @property
    def is_current_absence(self):
        """ Returns True is the absence is not closed and
        False in the other cases.
        """
        return not bool(self.end_date)

atapi.registerType(Absence, PROJECTNAME)
