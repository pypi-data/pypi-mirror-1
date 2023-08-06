from zope.i18nmessageid import MessageFactory
DebugInfoPortletMessageFactory = MessageFactory('collective.portlet.debuginfo')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
