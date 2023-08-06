from zope.i18nmessageid import MessageFactory
LinkPortletMessageFactory = MessageFactory('collective.portlet.links')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
