from zope.interface import Interface
from zope.schema import Date
from zope.annotation.interfaces import IAttributeAnnotatable

from redomino.autodelete import autodeleteMessageFactory as _

class IExpires(Interface):
    """ Expirable schema forms """
    delete_date = Date(title=_(u'Absolute delete date'),
                       description=_(u'Put here the delete date (format: YYYY-MM-DD)'),
                       required=True)
    def to_be_deleted(self):
        """ Returns True if the element is expired """

    def flush(self):
        """ Flush and reindex metadata attributes """


class IExpirable(IAttributeAnnotatable):
    """ Marker interface for expirable objects and can be annotable """

