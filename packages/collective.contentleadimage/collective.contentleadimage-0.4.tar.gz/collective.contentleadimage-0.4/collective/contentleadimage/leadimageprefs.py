from zope.interface import Interface, implements, Attribute
from zope.component import adapts
from zope.component import getUtility
from zope.interface import classImplements
from zope.interface import implementedBy

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.formlib import form
from zope import schema
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFCore.interfaces._tools import ITypesTool

from interfaces import ILeadImageable
from collective.contentleadimage import LeadImageMessageFactory as _

class ILeadImagePrefsForm(Interface):    
    """ The view for LeadImage  prefs form. """

    # remove and uncomment schema.Tuple below as soon as setting is working
    allowed_types = Attribute("Types")

    """
    allowed_types = schema.Tuple(title=_(u'Portal types'),
                          description=_(u'Portal types allowed to store lead image'),
                          missing_value=tuple(),
                          value_type=schema.Choice(
                                   vocabulary="plone.app.vocabularies.UserFriendlyTypes"),
                          required=False)
    """
    
    image_width = schema.Int(title=_(u'Width'),
                       description=_(u'Lead image width'),
                       default=67,
                       required=True)

    image_height = schema.Int(title=_(u'Height'),
                       description=_(u'Lead image height'),
                       default=81,
                       required=True)

                          


class LeadImageControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel adapter """

    adapts(IPloneSiteRoot)
    implements(ILeadImagePrefsForm)
    
    def __init__(self, context):
        super(LeadImageControlPanelAdapter, self).__init__(context)
        pprop = getUtility(IPropertiesTool)
        self.cli_props = pprop.cli_properties

    def get_image_height(self):
        return self.cli_props.image_height

    def set_image_height(self, image_height):
        self.cli_props.image_height = image_height
    
    def get_image_width(self):
        return self.cli_props.image_width

    def set_image_width(self, image_width):
        self.cli_props.image_width = image_width
    
    def get_allowed_types(self):
        return self.cli_props.allowed_types

    def set_allowed_types(self, allowed_types):
        """
        This code does not work yet. Please help to get it working.
        """
        # this is ok
        self.cli_props.allowed_types = allowed_types
        # there should be added ILeadImageable interface to selected types
        
        types_tool = getToolByName(self.context, 'portal_types')
        atool = getToolByName(self.context, 'archetype_tool')
        types_voc = getUtility(IVocabularyFactory, 'plone.app.vocabularies.UserFriendlyTypes')(self.context)
        for t in types_voc:
            key = t.value
            fti = types_tool.getTypeInfo(key)
            product = fti.product
            meta_type = fti.content_meta_type
            klass = atool.lookupType(product, meta_type)['klass']
            if key in allowed_types:
                # add it
                classImplements(klass, ILeadImageable)
            else:
                current = implementedBy(klass)
                all = current.interfaces()
                if ILeadImageable in all:
                    # remove
                    all.remove(ILeadImageable)
                    ifs = [i for i in all if i is not ILeadImageable]
                    classImplements(klass, ifs)
    
    image_height  = property(get_image_height, set_image_height)
    image_width   = property(get_image_width, set_image_width)
    allowed_types = property(get_allowed_types, set_allowed_types)

    
class LeadImagePrefsForm(ControlPanelForm):
    """ The view class for the lead image preferences form. """

    implements(ILeadImagePrefsForm)
    form_fields = form.FormFields(ILeadImagePrefsForm)

    label = _(u'Content Lead Image Settings Form')
    description = _(u'Select properties for Content Lead Image')
    form_name = _(u'Content Lead Image Settings')
            
        
        
        