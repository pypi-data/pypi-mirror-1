from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IMultiFileLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
    
class IMultiFileExtendable(Interface):
    """ Marker interface for multi file extending """