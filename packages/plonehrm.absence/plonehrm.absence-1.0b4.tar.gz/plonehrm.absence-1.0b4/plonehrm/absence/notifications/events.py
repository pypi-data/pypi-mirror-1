from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from plonehrm.absence.notifications.interfaces import IAbsenceEvent
from plonehrm.absence.utils import localize


class AbsenceEvent(ObjectEvent):
    implements(IAbsenceEvent)
    # This needs to be handled by a (HRM) Manager, e.g. a checklist
    # item specifically for managers needs to be created.
    for_manager = True
    def __init__(self, *args, **kwargs):
        super(AbsenceEvent, self).__init__(*args)
        self.message = localize(self.object, kwargs['subject'])


class AbsenceWeek1Event(AbsenceEvent):
    """First week of absence notification.
    """
    pass


class AbsenceWeek6Event(AbsenceEvent):
    """Fifth week of absence notification.
    """
    pass


class AbsenceWeek8Event(AbsenceEvent):
    """Eighth week of absence notification.
    """
    pass


class Absence6WeekRepeatEvent(AbsenceEvent):
    """Six week repeat absence notification.
    """
    def __init__(self, *args, **kwargs):
        super(Absence6WeekRepeatEvent, self).__init__(*args, **kwargs)
        create_url = self.object.absolute_url() + "/createObject?type_name=JobPerformanceInterview"
        self.message = """<a href="%s">%s</a>""" % (create_url, self.message)

        
        
        
