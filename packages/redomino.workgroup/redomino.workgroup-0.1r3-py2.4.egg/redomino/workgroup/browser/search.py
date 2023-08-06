from zope.interface import implements
from Products.PlonePAS.interfaces.browser import IPASSearchView
from Products.PlonePAS.browser.search import PASSearchView as PASDefaultSearchView
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.CMFCore.utils import getToolByName

from redomino.workgroup.interfaces import IWorkgroup
from redomino.workgroup.config import WORKGROUP_MEMBERDATA

class PASSearchView(PASDefaultSearchView):
    implements(IPASSearchView)

    def searchUsers(self, sort_by=None, **criteria):
                
        results = PASDefaultSearchView.searchUsers(self, sort_by, **criteria)

        if IPloneSiteRoot.providedBy(self.context):
            # per il plone site, tutti i risultati NON filtrati
            return results
        elif IWorkgroup.providedBy(self.context):
            # solo i risultati relativi al wg su cui mi trovo
            # TODO: mostrare anche gli utenti globali (presenti in portal_memberdata!)
            filter_path = self.context.absolute_url() + '/' + WORKGROUP_MEMBERDATA 
            filtered_users = filter(lambda x: filter_path in x['editurl'], results)
            # we need to pass the user from here to let local users manage a workgroup
            portal_membership = getToolByName(self.context, 'portal_membership')
            for user_dict in filtered_users:
                user = portal_membership.getMemberById(user_dict['userid'])
                if user:
                    user_dict['user'] = user
            return filtered_users
                
        else:
            # in tutti gli altri contenti, filtro via TUTTI gli elementi che contengono 
            # nel path WORKGROUP_MEMBERDATA
            filter_path = WORKGROUP_MEMBERDATA
            return filter(lambda x: filter_path not in x['editurl'], results)
            
        return results
