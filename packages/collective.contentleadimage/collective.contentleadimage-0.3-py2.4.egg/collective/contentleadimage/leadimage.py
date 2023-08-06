from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import adapts
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher import NotFound

from StringIO import StringIO

from OFS.Image import Image

from Products.Five.formlib.formbase import EditForm
from Products.Archetypes.interfaces import IBaseObject
from zope.app.form.browser.textwidgets import FileWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import scale_image
from Products.CMFPlone.interfaces import IPloneSiteRoot


from collective.contentleadimage.browser.widgets import LeadImageWidget
from collective.contentleadimage.interfaces import ILeadImage, ILeadImageable
from collective.contentleadimage.config import CONTENT_LEADIMAGE_ANNOTATION_KEY
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from collective.contentleadimage import LeadImageMessageFactory as _

# parts of code taken from http://svn.plone.org/svn/collective/ZipFileTransport/branches/cosl-plone3/

class LeadImageTraverse(DefaultPublishTraverse):
    implements(IPublishTraverse)
    adapts(ILeadImageable, IHTTPRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def publishTraverse(self, request, name):
        if name == 'leadimage':
            adp = ILeadImage(self.context)
            image = adp.img
            if image is not None:
                return image.__of__(self.context)
            else:
                raise NotFound, name
        else:
            return super(LeadImageTraverse, self).publishTraverse(request, name)
    

class LeadImageAdapter(object):
    implements(ILeadImage)
    adapts(ILeadImageable)
    
    def __init__(self, context):
        self.context = context

    def _get_img(self):
        ann = IAnnotations(self.context)
        image = ann.get(CONTENT_LEADIMAGE_ANNOTATION_KEY, None)
        if image is not None and image.has_key('data'):
            i = Image('leadimage', '', image['data'], image['contenttype'])
            return i
        return None

    def _set_img(self, value):
        pass
    
    def getImage(self):
        return self.img

    def setImage(self, imagedata):
        portal = getUtility(IPloneSiteRoot)
        props = ILeadImagePrefsForm(portal)
        ann = IAnnotations(self.context)
        # scale to defined size
        new_image, new_contenttype = scale_image(imagedata, (props.image_width,props.image_height))
        data = {'data':new_image.getvalue(), 'contenttype':new_contenttype}
        ann[CONTENT_LEADIMAGE_ANNOTATION_KEY] = data
        
    def removeImage(self):
        ann = IAnnotations(self.context)
        ann[CONTENT_LEADIMAGE_ANNOTATION_KEY] = {}

    img = property(_get_img, _set_img)
    
class LeadImageEditForm(EditForm):
    form_fields = form.FormFields(ILeadImage)
    form_fields['img'].custom_widget = LeadImageWidget
    label = _(u'Lead image')
    description = _(u'Lead image for the current object')
    
    @form.action(_(u'label_upload', default=_(u'Upload image')), name=u'Upload')
    def action_upload(self, action, data):
        file_obj = self.request.get('form.img')
        adp = ILeadImage(self.context)
        if file_obj.filename == '':
            # remove image
            adp.removeImage()
        else:
            file_obj.seek(0)
            adp.setImage(file_obj)        
        self.request.response.redirect('./view')
        
    