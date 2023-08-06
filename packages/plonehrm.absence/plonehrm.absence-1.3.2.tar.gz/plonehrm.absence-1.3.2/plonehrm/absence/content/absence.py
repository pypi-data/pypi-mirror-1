"""Definition of the Absence content type
"""

from datetime import date, timedelta

from Acquisition import aq_chain, aq_parent
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from persistent import Persistent
from zope.annotation.interfaces import IAnnotations
from zope import component

from plonehrm.absence import AbsenceMessageFactory as _
from plonehrm.absence.interfaces import IAbsence
from Products.plonehrm.interfaces import IEmployee
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

    atapi.FloatField(
        name='absence_length',
        widget=atapi.IntegerWidget(
            label=_(u'label_days_absent', default=u'Absence length (days)'),
        )
    ),

    atapi.BooleanField(
        name='is_accident',
        storage = atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'heading_accident', default=u'Due to an accident'),
        )
    ),

    atapi.FloatField(
        name='first_day_percentage',
        default = 1,
        vocabulary = ['0.25', '0.5', '0.75', '1'],
        widget=atapi.SelectionWidget(
            label=_(u'label_first_day_percentage',
                    default=u'Percentage of unworked time on first day'),
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


class AbsencePercentage(Persistent):
    """ This class defines an percentage of absence and productivity
    for an employee at a given time.
    """

    def __init__(self,                 
                 date=None,
                 absence=100,
                 productivity=0,
                 id=None):
        self.date = date
        self.absence = absence
        self.productivity = productivity
        self.id = id

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
    is_accident = atapi.ATFieldProperty('is_accident')

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

    def days_absent(self, arbo=False, start_date=None, end_date=None):
        """How long did the absence take?

        If the absence has ended, return the length stored on the
        object. Else try to estimate the number of days someone hasn't
        worked.

        Note 1: if the start date of the absence is in the future,
        return 1.

        Note 2: due to the way the algorithm works, should the
        employee works a 0 hour/day contract the employee will get 0
        sick days by his/her name when they are sick or were sick.

        If the 'arbo' parameter is set to True, we use th arbo_days_absent
        method instead (see below)
        """
        if arbo:
            return self.arbo_days_absent(start_date, end_date)
            
        if self.end_date:
            try:
                length = float(self.get('absence_length', 0))
            except (ValueError, TypeError):
                length = 0

            return length

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
        days_per_week = 0
        if current is not None:
            days_per_week = current.getDaysPerWeek()
        if days_per_week == 0:
            days_per_week = 5

        absence_length = float(end_date.toordinal() -
                               self.start_date.toordinal() + 1)
        sickness_days = (days_per_week / 7.0) * absence_length
        rounded_sickness = int(round(sickness_days))
        return rounded_sickness - (1 - self.get_first_day_percentage())

    def arbo_days_absent(self, start_date, end_date):
        """ This method does the same job than days_absent(), except that
        the algorithm is based on the way days are spread in the contract.
        This way, the result provided is really the number of absence days,
        not an evaluation.
        Of course, if contracts/letter do not have spread days, it does not
        work.

        If no start/end date is provided, we use the ones from the absence
        (and today as end date is the absence is not closed).
        Those two parameters are used to restrict computing (for example,
        compute absence days for the month of june, even if the absence covers
        may, june and july).
        """

        if not start_date or \
               start_date.toordinal() < self.start_date.toordinal():
            start_date = self.start_date
            first_day_correction = 1 - self.get_first_day_percentage()
        else:
            first_day_correction = 0

        if not end_date or not self.end_date or \
               end_date.toordinal() > self.end_date.toordinal():
            end_date = self.end_date and self.end_date or date.today()

        employee = aq_parent(self)

        # We use the employee worked days to know when he was absent,
        # as we restrict the period to the absence.
        absence_days = employee.get_worked_days(start_date, end_date)

        # We check that the employee really had to work on the first
        # day of absence to eventually correct the final value.
        first_absence_day = date(self.start_date.year,
                                 self.start_date.month,
                                 self.start_date.day)

        if first_absence_day in absence_days:
            if not absence_days[first_absence_day]:
                first_day_correction = 0
        else:
            first_day_correction = 0           

        # Now, we count the number of 'True' in the dictionnary to
        # know how long the absence was.        
        return len([absent for absent in absence_days
                    if absence_days[absent]]) - first_day_correction

    @property
    def is_current_absence(self):
        """ Returns True is the absence is not closed and
        False in the other cases.
        """
        return not bool(self.end_date)

    @property
    def percentage_list(self):
        """ Returns the list of absence/productivity percentage
        for this absence.
        """
        anno_key = 'plonehrm.absence'
        annotations = IAnnotations(self)
        
        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        if not 'percentage_list' in metadata:
            metadata['percentage_list'] = PersistentList()

        return metadata['percentage_list']

    @property
    def next_percentage_id(self):
        """ Returns the list of absence/productivity percentage
        for this absence.
        """
        anno_key = 'plonehrm.absence'
        annotations = IAnnotations(self)
        
        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        if not 'next_percentage_id' in metadata:
            metadata['next_percentage_id'] = 0
            return 0

        metadata['next_percentage_id'] += 1
        return metadata['next_percentage_id']


    def add_percentage(self, date, absence, productivity):
        """ Add a new absence/productivity percentage to the absence.
        """
        percentage_list = self.percentage_list
        id = self.next_percentage_id

        percentage = AbsencePercentage(date, absence, productivity, id)
        percentage_list.append(percentage)

    def current_percentage(self):
        """ Returns the current percentage of productivity/absence.
        """        
        percentage_list = self.percentage_list
        if not percentage_list:
            percentage_list.append(AbsencePercentage(date=self.start_date,
                                                     id=0))

        return percentage_list[-1]

    def get_first_day_percentage(self):
        try:
            return float(self.first_day_percentage)
        except (ValueError, TypeError, AttributeError):
            return 1

atapi.registerType(Absence, PROJECTNAME)
