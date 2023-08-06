# -*- coding: utf-8 -*-
#
# File: auto_delete.py
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

import logging
from DateTime import DateTime

from zope.interface import implements
from zope.component import queryUtility
from zope.app.component.hooks import getSite

from Acquisition import aq_parent
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from redomino.autodelete.utils.interfaces import IAutoDelete
from redomino.autodelete.utils.interfaces import IAutoDeleteQuery

class AutoDeleteQuery(object):
    """ AutoDeleteQuery implementation """
    implements(IAutoDeleteQuery)
    
    _query = {'to_be_deleted':True}

    @property
    def query(self):
        return self._query

class AutoDelete(object):
    implements(IAutoDelete)

    def run_autodelete(self):
        """ Auto-deletes all objects expired (with autodelete actived and with delete_date < now) """
        site = getSite()

        portal_catalog = getToolByName(site, 'portal_catalog')

        logger = logging.getLogger('redomino.autodelete')

        query_utility = queryUtility(IAutoDeleteQuery)
        if query_utility:
            query = query_utility.query
        else:
            # default query
            query = {'to_be_deleted':True}
        results = portal_catalog.searchResults(**query)
        if results:
            for result_brain in results:
                current_title = result_brain.Title
                current_path = result_brain.getPath()
                current_delete_date = result_brain.delete_date
    
                current_obj = result_brain.getObject()
                parent = aq_parent(aq_inner(current_obj))
                now = DateTime()
    
                try:
                    parent.manage_delObjects(ids=[current_obj.getId()])
                except Exception, e:
                    # log exception
                    log_exc = u'%s : %s [expired on %s] ERROR [%s]' % (current_path, current_title, current_delete_date, str(e))
                    logger.exception(log_exc)
                    yield log_exc
                else:
                    # log delete
                    log_inf = u'%s : %s [expired on %s] DELETED' % (current_path, current_title, current_delete_date)
                    logger.info(log_inf)
                    yield log_inf
    
    
