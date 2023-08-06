from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer


class IOrganization(Interface):
    """Marker interface
    """

class IOrganizationSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer 
       for this product.
    """
