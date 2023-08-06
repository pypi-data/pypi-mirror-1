from zope.i18nmessageid import MessageFactory

autodeleteMessageFactory = MessageFactory('redomino.autodelete')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
