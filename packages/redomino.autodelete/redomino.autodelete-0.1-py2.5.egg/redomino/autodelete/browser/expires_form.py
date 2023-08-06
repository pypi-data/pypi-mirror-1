# -*- coding: utf-8 -*-
#
# File: expires_form.py
#
# Copyright (c) 2008 by []
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

from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.component import getMultiAdapter

from zope.formlib.form import FormFields
from zope.formlib.form import action

from Products.Five.formlib.formbase import EditForm
from Products.Five.formlib.formbase import PageForm
from Products.Five.browser import BrowserView

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from redomino.autodelete.interfaces import IExpires
from redomino.autodelete.interfaces import IExpirable
from redomino.autodelete import autodeleteMessageFactory as _

class ExpiresForm(EditForm):
    """ Edit annotations form """
    form_fields = FormFields(IExpires)

    label = _(u'Expires form settings')
    description = _(u'Expiration date.')
    form_name = _(u'Expires form settings')

class EnableExpiresCondition(BrowserView):
    """Returns True or False depending on whether the enable expires action is allowed
    on current context.
    """ 
    @property
    def _action_condition(self):
        context = self.context
        return not IExpirable.providedBy(context) and not IPloneSiteRoot.providedBy(context)

    def __call__(self):
        return self._action_condition

class DisableExpiresCondition(BrowserView):
    """Returns True or False depending on whether the disable expires action is allowed
    on current context.
    """
    @property
    def _action_condition(self):
        return IExpirable.providedBy(self.context)

    def __call__(self):
        return self._action_condition

class EnableExpiresForm(PageForm):
    """ Enable expiration form (autodelete) """
    form_fields = []

    label = _(u'Enable expires (autodelete)')
    description = _(u'This object once expired will be deleted')
    form_name = _(u'Enable expires form (autodelete)')

    @action(_(u'Enable autodelete'))
    def enable(self, action, data):
        context = self.context

        # this item will be marked with the IExpirable marker interface
        alsoProvides(context, IExpirable)
        adapted = IExpires(context, None)
        adapted._reindex()

        # redirect and status message
        status_message = _(u'Enabled autodelete for this item')
        url = getMultiAdapter((context, self.request),
                              name='absolute_url')()
        IStatusMessage(self.request).addStatusMessage( _(status_message), type='info')
        self.request.response.redirect(url)
        return ''

class DisableExpiresForm(PageForm):
    """ Disable expiration form (autodelete) """
    form_fields = []

    label = _(u'Disable autodelete')
    description = _(u'Turn off the delete_date expiration')
    form_name = _(u'Disable expires form (autodelete)')

    @action(_(u'Disable autodelete'))
    def disable(self, action, data):
        context = self.context

        # this no longer provides the IExpirable marker interface
        noLongerProvides(context, IExpirable)
        adapted = IExpires(context, None)
        # flush annotations and reindex
        adapted.flush()

        # redirect and status message
        status_message = _(u'Disabled autodelete for this item')
        url = getMultiAdapter((context, self.request),
                              name='absolute_url')()
        IStatusMessage(self.request).addStatusMessage( _(status_message), type='info')
        self.request.response.redirect(url)
        return ''

