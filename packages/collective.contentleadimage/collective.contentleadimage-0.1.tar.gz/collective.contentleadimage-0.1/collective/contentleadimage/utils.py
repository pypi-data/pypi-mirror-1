from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from collective.contentleadimage.interfaces import ILeadImage, ILeadImageable

def hasContentLeadImage(object, portal, **kw):
    if ILeadImageable.providedBy(object):
        image = ILeadImage(object).getImage()
        return not not image
    return False

registerIndexableAttribute('hasContentLeadImage', hasContentLeadImage)
