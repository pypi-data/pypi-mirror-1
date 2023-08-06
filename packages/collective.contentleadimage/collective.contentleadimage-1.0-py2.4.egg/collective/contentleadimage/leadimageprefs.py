from zope.interface import Interface, implements, Attribute
from zope.component import adapts
from zope.component import getUtility
from zope.interface import classImplements
from zope.interface import implementedBy

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.formlib import form
from zope import schema
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
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

    image_maxwidth = schema.Int(title=_(u'Maximum width'),
                       description=_(u'Image maximum width. All uploaded images '
                                     u'will be scaled to this width/height'),
                       default=640,
                       required=True)

    image_maxheight = schema.Int(title=_(u'Maximum height'),
                       description=_(u'Image maximum height. All uploaded images '
                                     u'will be scaled to this width/height'),
                       default=480,
                       required=True)

    viewlet_description = schema.Bool(title=_(u'Show image next do Description field'),
                                  default=True,
                          )

    viewlet_body        = schema.Bool(title=_(u'Show image in body area'),
                                  default=False,
                          )


class LeadImageControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel adapter """

    adapts(IPloneSiteRoot)
    implements(ILeadImagePrefsForm)
    
    def __init__(self, context):
        super(LeadImageControlPanelAdapter, self).__init__(context)
        pprop = getUtility(IPropertiesTool)
        self.cli_props = pprop.cli_properties
        self.context = context

    def viewletVisible(self, manager, viewlet):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        hidden = storage.getHidden(manager, skinname)
        return viewlet not in hidden

    def setViewletVisibility(self, manager, viewlet, visible):
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        hidden = storage.getHidden(manager, skinname)
        if visible:
            # viewlet should be visible
            if viewlet in hidden:
                hidden = tuple(x for x in hidden if x != viewlet)
        else:
            # hide viewlet
            if viewlet not in hidden:
                hidden = hidden + (viewlet,)
        storage.setHidden(manager, skinname, hidden)
        

    def get_image_height(self):
        return self.cli_props.image_height

    def set_image_height(self, image_height):
        self.cli_props.image_height = image_height
    
    def get_image_width(self):
        return self.cli_props.image_width

    def set_image_width(self, image_width):
        self.cli_props.image_width = image_width
    
    def get_image_maxheight(self):
        return self.cli_props.image_maxheight

    def set_image_maxheight(self, image_maxheight):
        self.cli_props.image_maxheight = image_maxheight
    
    def get_image_maxwidth(self):
        return self.cli_props.image_maxwidth

    def set_image_maxwidth(self, image_maxwidth):
        self.cli_props.image_maxwidth = image_maxwidth
    
    def get_allowed_types(self):
        return self.cli_props.allowed_types

    def get_viewlet_description(self):
        manager = 'plone.belowcontenttitle'
        viewlet = 'collective.contentleadimage.thumbnail'
        return self.viewletVisible(manager, viewlet)

    def set_viewlet_description(self, value):
        manager = 'plone.belowcontenttitle'
        viewlet = 'collective.contentleadimage.thumbnail'
        self.setViewletVisibility(manager, viewlet, value)
        
    def get_viewlet_body(self):
        manager = 'plone.abovecontentbody'
        viewlet = 'collective.contentleadimage.full'
        return self.viewletVisible(manager, viewlet)

    def set_viewlet_body(self, value):
        manager = 'plone.abovecontentbody'
        viewlet = 'collective.contentleadimage.full'
        self.setViewletVisibility(manager, viewlet, value)
        
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
    image_maxheight  = property(get_image_maxheight, set_image_maxheight)
    image_maxwidth   = property(get_image_maxwidth, set_image_maxwidth)
    viewlet_description  = property(get_viewlet_description, set_viewlet_description)
    viewlet_body  = property(get_viewlet_body, set_viewlet_body)
    allowed_types = property(get_allowed_types, set_allowed_types)

    
class LeadImagePrefsForm(ControlPanelForm):
    """ The view class for the lead image preferences form. """

    implements(ILeadImagePrefsForm)
    form_fields = form.FormFields(ILeadImagePrefsForm)

    label = _(u'Content Lead Image Settings Form')
    description = _(u'Select properties for Content Lead Image')
    form_name = _(u'Content Lead Image Settings')
            
