from zope.interface import Interface
from zope.schema import Dict

from redomino.autodelete import autodeleteMessageFactory as _

class IAutoDelete(Interface):
    """ Autodelete utility interface"""

    def run_autodelete():
        """ Auto-deletes all objects expired (with autodelete actived and with delete_date < now) """

class IAutoDeleteQuery(Interface):
    """ Defines the catalog query for objects to be deleted """

    query = Dict(title=_(u'The query catalog for objects to be deleted'))

