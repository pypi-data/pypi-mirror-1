from Products.Five.browser import BrowserView

from redomino.workgroup.interfaces import IWorkgroup
from redomino.workgroupmemberarea.interfaces import IMemberArea

class WorkgroupConditionsView(BrowserView):
    """Returns True or False depending on whether the upload tab is allowed
    to be displayed on the current context.
    """

    def providesIWorkgroup(self):
        return IWorkgroup.providedBy(self.context)

    def providesIMemberArea(self):
        return IMemberArea.providedBy(self.context)

    def enable_wg_condition(self):
        """
        check if you could create a wg from obj
        """
        # TODO: vedere se obj e'callable
        #return obj.isPrincipiaFolderish() and not IWorkgroup.providedBy(obj)
        obj = self.context
        return not self.providesIWorkgroup(obj) and not self.providesIMemberArea(obj)

    def disable_wg_condition(self):
        """
        check if you could disable the wg on obj
        """
        obj = self.context
        return self.providesIWorkgroup(obj)


