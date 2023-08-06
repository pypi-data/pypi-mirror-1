from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager
 

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class IPortalWwpDate(IViewletManager):
  """A viewlet manager for pete's custom section displayed in header of rendered page  """

class IPortalAdBlockTop(IViewletManager):
  """A viewlet manager for pete's custom section displayed in header of rendered page  """



