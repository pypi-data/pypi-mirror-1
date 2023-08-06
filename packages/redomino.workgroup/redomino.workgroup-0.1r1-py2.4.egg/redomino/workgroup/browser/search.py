from zope.interface import implements
from Products.PlonePAS.interfaces.browser import IPASSearchView
from Products.PlonePAS.browser.search import PASSearchView as PASDefaultSearchView
from Products.CMFPlone.interfaces import IPloneSiteRoot

from redomino.workgroup.interfaces import IWorkgroup
from redomino.workgrouptool.content.workgroup_tool import WORKGROUP_MEMBERDATA

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
            return filter(lambda x: self.context.absolute_url() + '/' + WORKGROUP_MEMBERDATA in x['editurl'], results)
        else:
            # in tutti gli altri contenti, filtro via TUTTI gli elementi che contengono nel path WORKGROUP_MEMBERDATA
            return filter(lambda x: WORKGROUP_MEMBERDATA not in x['editurl'], results)
            
        return results

