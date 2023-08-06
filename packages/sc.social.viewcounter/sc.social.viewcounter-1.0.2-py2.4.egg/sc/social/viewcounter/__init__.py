from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory('sc.social.viewcounter')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
