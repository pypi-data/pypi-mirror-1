from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from collective.contentleadimage.interfaces import ILeadImage
from collective.contentleadimage.interfaces import ILeadImageable

class LeadImageViewlet(ViewletBase):
    render = ViewPageTemplateFile('leadimage.pt')

    def update(self):
        context = aq_inner(self.context)
        if ILeadImageable.providedBy(context):
            image = ILeadImage(context).getImage()
            # as soon as image is assigned to self.lead_image, it is not more Image, but <ImplicitAcquirerWrapper object at 0x....>
            self.lead_image = image
        else:
            self.lead_image = None
        
    def render(self, *args, **kwargs):
        context = aq_inner(self.context)
        image = getattr(self.lead_image, 'aq_self', self.lead_image)
        if image is not None:
            image = image.__of__(context)
            return image.tag(css_class="content-lead-image")
        else:
            return ''