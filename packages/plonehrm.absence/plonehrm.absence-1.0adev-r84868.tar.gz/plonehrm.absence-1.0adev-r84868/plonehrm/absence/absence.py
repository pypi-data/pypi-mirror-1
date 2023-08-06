from datetime import date

#from interfaces import IAbsence
from interfaces import IAbsenceAdapter
from persistent import Persistent
from persistent.list import PersistentList
from zope.interface import implements
from zope import component

from Products.plonehrm.interfaces import IEmployee
from plonehrm.absence.flags import NOTIFICATION_PREFIX
from plonehrm.notifications.interfaces import INotified


class Absence(Persistent):
    #implements(IAbsence)

    def __init__(self, text, start_date=None):
        super(Absence, self).__init__()
        self.text = text
        if start_date is None:
            start_date = date.today()
        self.start_date = start_date
        self.end_date = None

    def __cmp__(self, other):
        return cmp(self.start_date, other.start_date)

    def __repr__(self):
        value = "<Absence: %s, %s" % (self.text, self.start_date.isoformat())
        if self.end_date:
            value += " - " + self.end_date.isoformat()
        return value + ">"


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
        if not hasattr(self.context, 'absencelist'):
            self.context.absencelist = PersistentList()
        self.absencelist = self.context.absencelist

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
            start_date <= self.absencelist[-1].end_date):
            raise ConflictingStartDateError
        if start_date > date.today():
            raise StartDateInFutureError

        absence = Absence(text, start_date)
        self.absencelist.append(absence)
        self.absencelist.sort()
        return absence

    def close_absence(self, end_date, text=None):
        """Close the currently open absence."""
        assert(isinstance(end_date, date)), \
            'date expected, got %s' % type(end_date)

        absence = self.current_absence()
        assert(absence)
        if end_date < absence.start_date:
            raise CloseDateBeforeStartDateError
        absence.end_date = end_date
        if text:
            absence.text = text
        notified = INotified(self.context)
        notified.remove_notification_set(NOTIFICATION_PREFIX)
        return absence

    def remove_absence(self, index):
        """Remove absence ``index`` from the absencelist."""
        assert(len(self.absencelist) >= index + 1)
        return self.absencelist.pop(index)

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
