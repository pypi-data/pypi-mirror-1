from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class IPortalObject(Interface):
    pass

class IPloneBookmarkletsLayer(IDefaultBrowserLayer):
    """ A layer specific to this product
    """
