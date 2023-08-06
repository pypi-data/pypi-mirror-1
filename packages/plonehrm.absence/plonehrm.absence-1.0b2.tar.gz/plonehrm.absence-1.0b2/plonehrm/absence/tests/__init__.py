from Acquisition import Explicit
from Products.plonehrm.content.employee import Employee
from Products.plonehrm.interfaces import IEmployee
from plonehrm.absence.absence import AbsenceAdapter
from plonehrm.absence.notifications.interfaces import IAbsenceEvent
from plonehrm.notifications.adapters import Notified

from zope.annotation.attribute import AttributeAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import adapter, provideHandler
from zope.component import provideAdapter
from zope.interface import classImplements

# To make our event handler work in the tests.
import zope.component.event


class MockAQ(Explicit):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockEmployee(MockAQ, Employee):

    def getObject(self):
        """Testing hack: mock employees also act like a brain wrapper of
        themselves
        """
        return self


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

provideHandler(event_tracker)



# Since we don't load the ZCML in the doctests, we'll have to manually
# register some components
provideAdapter(AbsenceAdapter)
provideAdapter(AttributeAnnotations)
classImplements(MockEmployee, IAttributeAnnotatable)
provideAdapter(factory=Notified, adapts=[IEmployee])
