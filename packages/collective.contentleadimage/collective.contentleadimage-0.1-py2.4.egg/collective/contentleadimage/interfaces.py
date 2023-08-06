from zope import schema
from zope.interface import Interface

from schemas import ImageLine
from collective.contentleadimage import LeadImageMessageFactory as _

class ILeadImageable(Interface):
    """ marker interface """
    

class ILeadImage(Interface):

    img = ImageLine(title=_(u'Lead image'),
                    description=_('image_description', default=u"""You can upload lead image. This image will be displayed above 
                                    the content. Uploaded image will be automatically scaled to 
                                    size specified in the leadimage control panel. If you want to remove the image,
                                    do not select any file and press 'Upload image' button."""),
                    required=False)

    def getImage():
        """ 
        returns unwrapped Image object or None
        """    
    
    def setImage(imagedata):
        """ 
        takes file object and content type and stores passed data into annotation
        """
        
    def removeImage():
        """ removes image from the annotation """

class IFolderLeadSummaryView(Interface):
    
    def getLeadImageTag(obj):
        """ generate the tag """