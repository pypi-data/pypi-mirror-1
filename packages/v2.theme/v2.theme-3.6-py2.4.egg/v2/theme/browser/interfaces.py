from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "V2 Theme" theme, this interface must be its layer
       (in theme/viewlets/configure.zcml).
    """

class IFullViewManager(IViewletManager):
    """Viewlet manager on top of the full view on the expanded view
       used to show the table of contents
    """

class ISearchView(Interface):
    """Used to provide python functions to the search results
    """
    def isVideo(self, item):
	"""Tests if the item is a video
	"""
    def audio_only(self, item):
        """Test if is audio_only
	"""
