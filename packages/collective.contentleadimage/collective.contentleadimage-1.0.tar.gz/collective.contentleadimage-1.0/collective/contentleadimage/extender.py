from Products.Archetypes.public import ImageField
from archetypes.schemaextender.field import ExtensionField
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from Products.Archetypes.public import ImageWidget
from Products.CMFPlone.interfaces import IPloneSiteRoot

from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher import NotFound

from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage import LeadImageMessageFactory as _
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_MAX_SIZE
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

class LeadimageImageField(ExtensionField, ImageField):
    """A Image field. """

    @property
    def max_size(self):
        portal = getUtility(IPloneSiteRoot)
        cli_prefs = ILeadImagePrefsForm(portal)
        return (cli_prefs.image_maxwidth, cli_prefs.image_maxheight)
        

    @property
    def sizes(self):
        portal = getUtility(IPloneSiteRoot)
        cli_prefs = ILeadImagePrefsForm(portal)
        return {'leadimage': (cli_prefs.image_width, cli_prefs.image_height)}
        

class LeadImageExtender(object):
    adapts(ILeadImageable)
    implements(IOrderableSchemaExtender)


    fields = [
        LeadimageImageField(IMAGE_FIELD_NAME,
            widget = ImageWidget(
                         label=_(u"Lead image"),
                         description=_(u"You can upload lead image. This image "
                                       u"will be displayed above the content. "
                                       u"Uploaded image will be automatically "
                                       u"scaled to size specified in the leadimage "
                                       u"control panel."),
                 ),
        ),
            ]

    def __init__(self, context):
         self.context = context

    def getFields(self):
         return self.fields
         
    def getOrder(self, original):
        """
        'original' is a dictionary where the keys are the names of
        schemata and the values are lists of field names, in order.
        
        Move leadImage field just after the Description
        """
        default = original.get('default', None)
        if default:
            desc_index = default.index('description')
            if desc_index >= 0:
                default.remove(IMAGE_FIELD_NAME)
                default.insert(desc_index+1, IMAGE_FIELD_NAME)
        return original

class LeadImageTraverse(DefaultPublishTraverse):
    implements(IPublishTraverse)
    adapts(ILeadImageable, IHTTPRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def publishTraverse(self, request, name):
        if name.startswith(IMAGE_FIELD_NAME):
            field = self.context.getField(IMAGE_FIELD_NAME)
            if field is not None:
                image = None
                if name == IMAGE_FIELD_NAME:
                    image = field.getScale(self.context)
                else:
                    scalename = name[len(IMAGE_FIELD_NAME + '_'):]
                    if scalename in field.getAvailableSizes(self.context):
                        image = field.getScale(self.context, scale=scalename)
                if image is not None and not isinstance(image, basestring):
                    # image might be None or '' for empty images
                    return image

        return super(LeadImageTraverse, self).publishTraverse(request, name)
