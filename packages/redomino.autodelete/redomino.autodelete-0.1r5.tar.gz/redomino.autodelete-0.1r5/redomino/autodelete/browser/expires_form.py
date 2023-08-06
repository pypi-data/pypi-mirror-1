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

import datetime

from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides
from zope.component import adapts
from zope.component import getMultiAdapter

from zope.formlib.form import action

from plone.fieldsets.fieldsets import FormFieldsets
from plone.fieldsets.form import FieldsetsEditForm

from Products.Five.formlib.formbase import PageForm
from Products.Five.browser import BrowserView

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from redomino.autodelete.interfaces import IExpires
from redomino.autodelete.interfaces import IExpiresExtendedSchema
from redomino.autodelete.interfaces import IExpirable
from redomino.autodelete import autodeleteMessageFactory as _

#try:
#    from zc.datetimewidget.datetimewidget import DateWidget
#    DATETIMEWIDGET = True
#except:
#    DATETIMEWIDGET = False

class ExpiresExtendedSchema(SchemaAdapterBase):
    """ Extends the schema of IExpires and provides more methods to set the delete_date provided by IExpires """
    adapts(IExpirable)
    implements(IExpiresExtendedSchema)

    def __init__(self, context):
        super(ExpiresExtendedSchema, self).__init__(context)
        self.context = context

    def get_relative_days(self):
        now = datetime.datetime.now()
        adapted = IExpires(self.context, None)
        delete_date = adapted.delete_date
        days = 0
        if delete_date:
            delta = delete_date - now
            days = delta.days + 1
            if days < 0:
                days = 0
        else:
            return days
        return days

    def set_relative_days(self, value):
        if value:
            delta = datetime.timedelta(days=value)
            today = datetime.datetime.today()
            delete_date = today + delta 
    
            adapted = IExpires(self.context, None)
            adapted.delete_date = delete_date

    relative_days = property(get_relative_days, set_relative_days)


class FieldsetsEditFormMixin(FieldsetsEditForm):
    """ Mixin class with a fieldset template """
    template = ViewPageTemplateFile('templates/fieldset.pt')

#absolutedate_set = FormFieldsets(IExpires)
#if DATETIMEWIDGET:
#    absolutedate_set['delete_date'].custom_widget = DateWidget
#absolutedate_set['delete_date'].custom_widget = dtwidget
#
#absolutedate_set.id = 'absolute_date'
#absolutedate_set.label = _(u'Absolute delete date')

relativedate_set = FormFieldsets(IExpiresExtendedSchema)
relativedate_set.id = 'days'
relativedate_set.label = _(u'Days of validity')

class ExpiresForm(FieldsetsEditFormMixin):
    """ Edit annotations form """
    #form_fields = FormFieldsets(absolutedate_set, relativedate_set)
    form_fields = FormFieldsets(relativedate_set)

    label = _(u'Autodelete form settings')
    description = _(u'Here you can choose either an absolute delete date or a number of days of validity for this item.')
    form_name = _(u'Expires form settings')

    @property
    def delete_date(self):
        ## or better using schema extender??
        adapted = IExpires(self.context, None)
        delete_date = adapted.delete_date

        return delete_date
    

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

