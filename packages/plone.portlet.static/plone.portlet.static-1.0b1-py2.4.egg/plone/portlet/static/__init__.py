from zope.i18nmessageid import MessageFactory
StaticMessageFactory = MessageFactory('plone.portlet.static')

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
