from plonehrm.notifications.interfaces import IHRMModuleEvent
from plonehrm.notifications.interfaces import IHRMEmailer


class IPersonalDataEvent(IHRMModuleEvent):
    pass


class IPersonalDataEmailer(IHRMEmailer):
    pass
