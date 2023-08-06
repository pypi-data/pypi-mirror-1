from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from collective.flowplayer.interfaces import IFlowPlayable

class SearchView(BrowserView):

	def isVideo(self, item):
 		result = IFlowPlayable.providedBy(item)
 		return result

	def audio_only(self, item):
 	        result = IAudio.providedBy(item)
 	        return result
