from plonehrm.notifications.interfaces import IHRMModuleEvent
from plonehrm.notifications.interfaces import IHRMEmailer


class IAbsenceEvent(IHRMModuleEvent):
    pass


class IAbsenceEmailer(IHRMEmailer):
    pass
