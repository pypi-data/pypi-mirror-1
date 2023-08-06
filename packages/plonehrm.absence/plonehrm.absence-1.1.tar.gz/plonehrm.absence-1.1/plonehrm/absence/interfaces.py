from zope.interface import Interface


class IAbsence(Interface):
    """Absence"""


class IAbsenceFile(Interface):
    """Absence File"""


class IAbsenceAdapter(Interface):
    """Interface for the Absence adapter.
    This is used to get/set absence information on Employees.
    """

    def add_absence(text, start_date=None):
        """Add a new absence to the absencelist."""

    def close_absence(end_date):
        """Close the currently open absence."""

    def remove_absence(index):
        """Remove absence ``index`` from the absencelist."""

    def current_absence():
        """Return the unterminated absence."""

    def is_absent():
        """Test for an unterminated absence."""


class INote(Interface):
    """Notes to add to an absence"""


class IEvaluationInterview(Interface):
    """Interview done during absences."""
