from Acquisition import Explicit
from zope.component import adapter

from plonehrm.absence.notifications.interfaces import IAbsenceEvent


class MockAQ(Explicit):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockMailer(MockAQ):

    def __init__(self, employee, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.employee = employee

    def send(self):
        print self.template.pt_source_file(), self.employee, self.subject


@adapter(IAbsenceEvent)
def event_tracker(event):
    print event
