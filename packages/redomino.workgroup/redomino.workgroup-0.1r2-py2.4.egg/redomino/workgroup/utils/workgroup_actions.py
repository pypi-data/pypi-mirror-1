from zope.interface import implements
from zope.interface import noLongerProvides
from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from redomino.workgroup.interfaces import IWorkgroup
from redomino.workgroup.utils.interfaces import IWorkgroupActions

class WorkgroupActions(object):
    """ WorkgroupActions utility """
    implements(IWorkgroupActions)

    _WORKGROUP_MEMBERDATA = 'workgroup_memberdata'

    def disable(self, context):
        """ Disable workgroup action """

        noLongerProvides(context, IWorkgroup)
        if context.hasObject(self._WORKGROUP_MEMBERDATA):
             wg_memberdata = getattr(context, self._WORKGROUP_MEMBERDATA)
             wg_memberdata.unindexObject()

    def enable(self, context):
        """ Enable workgroup action"""

        portal_types = getToolByName(context, 'portal_types')

        try:
            if not context.hasObject(self._WORKGROUP_MEMBERDATA):
                portal_types.constructContent('MemberArea', context, self._WORKGROUP_MEMBERDATA)
            wg_memberdata = getattr(context, self._WORKGROUP_MEMBERDATA)
            

            wg_memberdata.unindexObject()
        except:
            raise
        else:
            alsoProvides(context, IWorkgroup)

