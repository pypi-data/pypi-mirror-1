from zope.i18nmessageid import MessageFactory
PayPalPortletMessageFactory = MessageFactory('collective.portlet.paypal')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
