# -*- coding: utf-8 -*-
#
# File: maintenance_utils.py
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
from StringIO import StringIO
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Acquisition import aq_inner

def runAutodelete(self):
    """ Delete expired contents """

    out = StringIO()

    portal = getToolByName(self, 'portal_url').getPortalObject()
    portal_catalog = getToolByName(portal, 'portal_catalog')

    logger = logging.getLogger('redomino.autodelete')


    print >> out, "START"

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
            print >> out, "[%s] %s : %s [expired on %s]" % (now, current_path, current_title, current_delete_date)
    
            try:
                parent.manage_delObjects(ids=[current_obj.getId()])
            except Exception, e:
                print >> out, "[%s] %s : %s [expired on %s] ERROR [%s]" % (now, current_path, current_title, current_delete_date, str(e))
                # log exception
                logger.exception("%s : %s [expired on %s] ERROR [%s]" % (current_path, current_title, current_delete_date, str(e)))
            else:
                print >> out, "[%s] %s : %s [expired on %s] DELETED" % (now, current_path, current_title, current_delete_date)
                # log delete
                logger.info("%s : %s [expired on %s] DELETED" % (current_path, current_title, current_delete_date))
        print >> out, "DONE"
    else:
        print >> out, "No expired content has been found matching your request"

    return out.getvalue()


