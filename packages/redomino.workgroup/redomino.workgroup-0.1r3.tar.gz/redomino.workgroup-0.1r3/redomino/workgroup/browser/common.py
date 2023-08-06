from Products.Five.browser import BrowserView
from Products.Archetypes.interfaces._base import IBaseFolder

from redomino.workgroup.interfaces import IWorkgroup
from redomino.workgroup.interfaces import IMemberArea

class EnableWorkgroupCondition(BrowserView):
    """Returns True or False depending on whether the enable workgroup action is allowed
    on current context.
    """
    @property
    def _action_condition(self):
        return IBaseFolder.providedBy(self.context) and not IWorkgroup.providedBy(self.context) and not IMemberArea.providedBy(self.context)

    def __call__(self):
        return self._action_condition

class DisableWorkgroupCondition(BrowserView):
    """Returns True or False depending on whether the disable workgroup action is allowed
    on current context.
    """
    @property
    def _action_condition(self):
        return IWorkgroup.providedBy(self.context)

    def __call__(self):
        return self._action_condition

