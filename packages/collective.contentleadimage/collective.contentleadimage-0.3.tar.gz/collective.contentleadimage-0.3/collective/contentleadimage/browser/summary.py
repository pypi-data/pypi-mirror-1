from zope.interface import implements
from zope.component import getUtility 
from zope.component import queryAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage.interfaces import ILeadImage
from collective.contentleadimage.interfaces import IFolderLeadSummaryView

from Products.CMFPlone.utils import base_hasattr

class FolderLeadSummaryView(BrowserView):
    implements(IFolderLeadSummaryView)
    
    def getLeadImageTag(self, obj):
        """ """
        portal_type = obj.portal_type
        if ILeadImageable.providedBy(self.context):
            adp = ILeadImage(obj)
            img = adp.getImage()
            if img is not None:
                img = img.__of__(obj)
                return img.tag(css_class="leadimage-summary")
        return None

