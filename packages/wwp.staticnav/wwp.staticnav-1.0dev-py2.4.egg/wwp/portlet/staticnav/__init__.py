from zope.i18nmessageid import MessageFactory
static_navMessageFactory = MessageFactory('wwp.staticnav')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
