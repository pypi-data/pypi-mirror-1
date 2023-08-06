from datetime import date

from interfaces import IAbsenceAdapter
from zope.interface import implements
from zope.event import notify
from zope import component

from Products.Archetypes.event import ObjectInitializedEvent
from Products.plonehrm.interfaces import IEmployee
from plonehrm.absence.flags import NOTIFICATION_PREFIX
from plonehrm.notifications.interfaces import INotified


class AbsenceDateError(Exception):

    def __str__(self):
        return u"Date Error"


class ConflictingStartDateError(AbsenceDateError):

    def __str__(self):
        return u"Error: Conflicting start date"


class StartDateInFutureError(AbsenceDateError):

    def __str__(self):
        return u"Error: Start date in future"


class CloseDateBeforeStartDateError(AbsenceDateError):

    def __str__(self):
        return u"Error: Close date before start date"


class AbsenceAdapter(object):
    """This adapter can be used to get/set absence information on Employees.
    """
    implements(IAbsenceAdapter)
    component.adapts(IEmployee)

    def __init__(self, context):
        self.context = context

    @property
    def absencelist(self):
        contentFilter = {'portal_type': 'Absence'}
        brains = self.context.getFolderContents(contentFilter=contentFilter)
        objects = [brain.getObject() for brain in brains]

        def date_key(item):
            return item['start_date']

        items = sorted(objects, key=date_key)
        return items

    def add_absence(self, text, start_date=None):
        """Add a new absence to the absencelist."""
        assert(not self.is_absent()), \
            'there can only be one open absence'
        assert(isinstance(text, basestring)), \
            'string expected, got %s' % type(text)
        assert(start_date is None or
               isinstance(start_date, date)), \
            'date expected, got %s' % type(start_date)

        # Make sure we have a valid start date.
        if start_date is None:
            start_date = date.today()
        if (self.absencelist and
            start_date.toordinal() <= \
                self.absencelist[-1].end_date.toordinal()):
            raise ConflictingStartDateError
        if start_date.toordinal() > date.today().toordinal():
            raise StartDateInFutureError

        #absence = Absence(text, start_date)
        #self.absencelist.append(absence)
        #self.absencelist.sort()

        new_id = self.context.generateUniqueId('Absence')
        self.context.invokeFactory('Absence',
                                   id=new_id,
                                   title=text)
        new_absence = getattr(self.context, new_id)
        new_absence.start_date = start_date
        new_absence.unmarkCreationFlag()
        new_absence._renameAfterCreation()
        notify(ObjectInitializedEvent(new_absence))

        return new_absence

    def close_absence(self, end_date, length=None, text=None):
        """Close the currently open absence."""
        assert(isinstance(end_date, date)), \
            'date expected, got %s' % type(end_date)
        absence = self.current_absence()
        assert(absence)
        if end_date.toordinal() < absence.start_date.toordinal():
            raise CloseDateBeforeStartDateError
        absence.end_date = end_date
        if text:
            absence.text = text
        if length is not None:
            absence.absence_length = length
        else:
            absence.absence_length = absence.days_absent()
        notified = INotified(self.context)
        notified.remove_notification_set(NOTIFICATION_PREFIX)
        return absence

    def remove_absence(self, index):
        """Remove absence ``index`` from the absencelist."""
        assert(len(self.absencelist) >= index + 1)
        to_remove = self.absencelist.pop(index)
        self.context._delObject(to_remove.id)
        return to_remove

    def current_absence(self):
        """Return the unterminated absence."""
        for absence in self.absencelist:
            if not absence.end_date:
                return absence

    def is_absent(self):
        """Test for an unterminated absence."""
        if self.current_absence():
            return True
        return False
