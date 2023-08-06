from zope.interface import Interface

from zope.schema import Date
from zope.schema import Int
from zope.schema import Choice
from zope.annotation.interfaces import IAttributeAnnotatable

from redomino.autodelete import autodeleteMessageFactory as _

class IExpiresExtendedSchema(Interface):
    """ This interface provides more ways to choose the delete_date """
    relative_days = Choice(title=_(u'Days of validity'),
                           description=_(u'You can choose the number of days of validity. After this term your object will be deleted'),
                           vocabulary='redomino.autodelete.vocabularies.relativedays',
                           required=False)


class IExpires(Interface):
    """ Expirable adapter for auto-delete objects enabled """
    delete_date = Date(title=_(u'Absolute delete date'),
                       description=_(u'Put here the delete date (format: YYYY-MM-DD)'),
                       required=False)
    def to_be_deleted():
        """ Returns True if the element is expired """

    def flush():
        """ Flush and reindex metadata attributes """


class IExpirable(IAttributeAnnotatable):
    """ Marker interface for expirable objects (objects that could be deleted automatically) and can be annotable """

class IAutodeleteControlPanel(Interface):
    """ Marker interface for the AutodeleteControlPanel """

    def delete():
        """ Delete action """

