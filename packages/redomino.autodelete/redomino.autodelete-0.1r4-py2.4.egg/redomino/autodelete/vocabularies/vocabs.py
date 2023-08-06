from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from redomino.autodelete import autodeleteMessageFactory as _

class RelativeDaysVocab(object):
    """ Vocabulary that returns a list of integers (number if days) """ 
    implements(IVocabularyFactory)

    _days = range(1,30)

    def __call__(self, context):
        items = [(_(u'%d days' % item), item) for item in self._days]
        return SimpleVocabulary.fromItems(items)
    
relativedays_factory = RelativeDaysVocab()

