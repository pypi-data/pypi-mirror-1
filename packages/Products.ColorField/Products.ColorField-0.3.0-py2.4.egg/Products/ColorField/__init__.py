from Products.ColorField._field import ColorField, ColorWidget
from zope.i18nmessageid import MessageFactory

ColorFieldMessageFactory = MessageFactory('Products.ColorField')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
