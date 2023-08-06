from zope.i18nmessageid import MessageFactory
OverrideSharingMessageFactory = MessageFactory('atreal.override.sharing')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
