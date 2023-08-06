import time
import string
from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from Products.CMFCore.utils import getToolByName


class ExpandedView(BrowserView):
    
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class)
        return ''

    def currenttime(self):
	return time.time()
    
    def trimDescription(self, desc):
	if len(desc) > 250: 
		res = desc[0:250]
		lastspace = res.rfind(" ")
		res = res[0:lastspace] + " ..."
		return res
	else:
		return desc

    def isPublishable(self, item):
	if item.getPortalTypeName() == 'File' or item.getPortalTypeName() == 'Image':
		return False
	else:
		return True

    def getRelatedItemsByType(self, type):
	related = self.context.getRelatedItems()
	backRelated = self.context.getBRefs()
	result = []	
	workflow = getToolByName(self, 'portal_workflow')
	member = getToolByName(self, 'portal_membership')
	
	for backItem in backRelated:
		if backItem.getPortalTypeName() == type and (not self.isPublishable(backItem) or workflow.getInfoFor(backItem, 'review_state') == 'published' or not member.isAnonymousUser()):
		#if backItem.getPortalTypeName() == type:
			if not (backItem in  related):
				result.append(backItem)
	for item in related:
		if item.getPortalTypeName() == type and (not self.isPublishable(item) or workflow.getInfoFor(item, 'review_state') == 'published' or not member.isAnonymousUser()):
		#if item.getPortalTypeName() == type:
			result.append(item)
	
	return result	

    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        try:
            return util.ulocalized_time(time, long_format, time_only, self.context,
                                        domain='plonelocales')
        except TypeError: # Plone 3.1 has no time_only argument
            return util.ulocalized_time(time, long_format, self.context,
                                        domain='plonelocales')

    def creator(self):
        return self.context.Creator()

    def author(self):
	return 0

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()
