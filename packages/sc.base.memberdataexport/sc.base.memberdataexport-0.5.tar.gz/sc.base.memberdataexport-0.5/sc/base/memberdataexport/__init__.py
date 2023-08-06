from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory('sc.base.memberdataexport')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
