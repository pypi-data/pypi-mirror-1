from Products.Five.browser import BrowserView
from Products.Five.formlib.formbase import PageForm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class MemberAreaView(BrowserView):
    __call__ = ViewPageTemplateFile('templates/memberarea_view.pt')

class MemberListingView(BrowserView):
    __call__ = ViewPageTemplateFile('templates/member_listing.pt')


