# -*- coding: utf-8 -*-
#
# File: launch_autodelete.py
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

from zope.interface import implements
from zope.component import queryUtility

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from redomino.autodelete import autodeleteMessageFactory as _
from redomino.autodelete.interfaces import IAutodeleteControlPanel
from redomino.autodelete.utils.interfaces import IAutoDelete

class AutodeleteControlPanel(BrowserView):
    """ AutodeleteControlPanel view """
    implements(IAutodeleteControlPanel)

    label = _(u'Autodelete control panel')
    description = _(u'You can run manually the autodelete task for element expired.')

    __call__ = ViewPageTemplateFile('templates/control-panel.pt')

    def delete(self):
        """ Delete task """
        response = self.request.response
        response.setHeader('Content-type', 'text/html')
        try:
            auto_delete = queryUtility(IAutoDelete)
            if auto_delete:
                for item in auto_delete.run_autodelete():
                    if isinstance(item, unicode):
                        response.write(item.encode() + '<br />')
                    else:
                        response.write(item + '<br />')
            response.write('Done')
        except Exception, e:
            response.write('An error was occurred: ' + str(e))



