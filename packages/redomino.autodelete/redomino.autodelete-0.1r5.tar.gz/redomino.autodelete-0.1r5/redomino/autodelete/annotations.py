# -*- coding: utf-8 -*-
#
# File: annotations.py
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

from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from redomino.autodelete.interfaces import IExpirable
from redomino.autodelete.interfaces import IExpires

class ExpiresAnnotation(object):
    """ Adapter for the metadata annotations """

    implements(IExpirable)
    _KEY = 'redomino.autodelete'
    _IDXS = ['absolote_date', 'to_be_deleted']

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self.metadata = annotations.get(self._KEY, None)
        if self.metadata is None:
            annotations[self._KEY] = PersistentDict()
            self.metadata = annotations[self._KEY]

    def _get_delete_date(self):
        """ Get the delete expiration date (datetime format)"""
        return self.metadata.get('delete_date', None)
    def _set_delete_date(self, date):
        """ Set the delete expiration date (datetime format)"""
        self.metadata['delete_date'] = date
        self._reindex()

    delete_date = property(_get_delete_date, _set_delete_date)

    def to_be_deleted(self):
        """ Returns True if the element is expired """
        delete_date = self.delete_date
        if not delete_date:
            return False
        return IExpirable.providedBy(self.context) and datetime.datetime.today() > delete_date

    def flush(self):
        """ Flush and reindex metadata attributes """
        self.delete_date = None
        self._reindex()

    def _reindex(self):
        """ Reindex metadata attributes when needed """
        self.context.reindexObject(idxs=self._IDXS)

def delete_date(object, portal, **kw):
    """ Register annotated property delete_date to get it into the catalog"""
    adapted = IExpires(object, None)
    if adapted is not None:
        delete_date = adapted.delete_date
        if delete_date and isinstance(delete_date, datetime.datetime):
            return delete_date.strftime('%Y-%m-%d %H:%M:%S')
    return None

registerIndexableAttribute('delete_date', delete_date)

def to_be_deleted(object, portal, **kw):
    """ Register annotated property to_be_deleted to get it into the catalog """
    adapted = IExpires(object, None)
    if adapted is not None:
         to_be_deleted = adapted.to_be_deleted()
         return to_be_deleted
    return None

registerIndexableAttribute('to_be_deleted', to_be_deleted)


