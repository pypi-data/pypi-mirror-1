from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer

class IInstantMessage(Interface):
    """Marker interface
    """

class IInstantMessageSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer 
       for this product.
    """
