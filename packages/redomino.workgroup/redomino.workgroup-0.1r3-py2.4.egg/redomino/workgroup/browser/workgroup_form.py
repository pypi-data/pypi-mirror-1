# -*- coding: utf-8 -*-
#
# File: workgroup_form.py
#
# Copyright (c) 2008 by Davide Moro (Redomino)
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Davide Moro <davide.moro@redomino.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.component import getMultiAdapter
from zope.component import queryUtility

from Products.Five.formlib.formbase import PageForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as _

from redomino.workgroup.interfaces import IWorkgroup
from redomino.workgroup.utils.interfaces import IWorkgroupActions

class WorkgroupEnableForm(PageForm):
    form_fields = []
    label = u'Enable workgroup management'

    @form.action("Enable workgroup")
    def enable_workgroup(self, action, data):
        # here I have to set the correct marker interface
        context = self.context
        
        wg_util = queryUtility(IWorkgroupActions)
        wg_util.enable(context)
        
        status_message = u'Enabled workgroup'
        url = getMultiAdapter((context, self.request),
                              name='absolute_url')()
        IStatusMessage(self.request).addStatusMessage( _(status_message), type='info')
        self.request.response.redirect(url)
        return ''

class WorkgroupDisableForm(PageForm):
    form_fields = []
    label = u'Disable workgroup management'

    @form.action("Disable workgroup")
    def disable_workgroup(self, action, data):
        # here I have to set the correct marker interface
        context = self.context
        
        if len(context.restrictedTraverse('@@pas_search').searchUsers()) > 0:
            status_message = u'workgroup not disabled: you must delete all workgroup users first!'
        else:
            wg_util = queryUtility(IWorkgroupActions)
            wg_util.disable(context)
            status_message = u'Disabled workgroup'
            
        url = getMultiAdapter((context, self.request),
                              name='absolute_url')()

        IStatusMessage(self.request).addStatusMessage( _(status_message), type='info')
        self.request.response.redirect(url)
        return '' 

