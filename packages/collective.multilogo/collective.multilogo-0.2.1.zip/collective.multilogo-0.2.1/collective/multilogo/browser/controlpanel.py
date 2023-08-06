from zope import schema
from zope.component import adapts, getMultiAdapter
from zope.formlib.form import FormFields
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget
from zope.app.form import CustomWidgetFactory
from zope.interface import implements
from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm

from collective.multilogo import multilogoMessageFactory as _

class ILogoAttrPair(Interface):
    logo_text = schema.TextLine(title=_(u"title"))
    logo_img  = schema.ASCIILine(title=(u"image"), required=False, default='')
    logo_link = schema.TextLine(title=_(u"link"), required=False, default=u'')
    css_class = schema.TextLine(title=_(u"css class"), required=False, default=u'')
    new_win   = schema.Bool(title=_(u"new window"), required=False, default=False)
    separator = schema.ASCIILine(title=_(u"separator"),required=False, default='')

class LogoAttrPair:
    implements(ILogoAttrPair)
    def __init__(self, text=u'', img='', link=u'', css_class=u'', new_win=False, separator = ''):
        self.logo_text = text
        self.logo_img  = img
        self.logo_link = link
        self.css_class = css_class
        self.new_win   = new_win
        self.separator = separator

class IMultiLogoSchema(Interface):
    """
    """
    display_inline = schema.Bool(
        title=_(u"Display Inline"),
        description=_("If checked, logo items defined below will be displayed in one line, otherwise each logo item (including separator) will be rendered on new line."),
        default=True
    )
        
    logo_items = schema.List(
        title=_("Logo items"),
        description=_(u'help_logo_items',
            default=u"Define logo items, each as pack of the following"
                     " attributes: title (required)- text to render as logo"
                     " if no image is defined, image - name of the image"
                     " object placed somewhere in the portal, link - url"
                     " to render logo as active link, css class - assign"
                     " individual css class to the logo item to be able to"
                     " manage its look and feel, new window - if checked and"
                     " link is defined, target url will be openned in the"
                     " new browser window."),
        required=True,
        value_type=schema.Object(ILogoAttrPair, title=_(u"Logo items")),
    )
   
    promo_line = schema.TextLine(
            title=_(u"Promo text"), 
            description=_(u'help_promo_line',
                default=u"Enter a text that appears below the logo."),
            required=False, default=u'')
   
class MultiLogoControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMultiLogoSchema)

    def __init__(self, context):
        super(MultiLogoControlPanelAdapter, self).__init__(context)
        self.portal = context
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.logo_properties

    def get_display_inline(self):
        return bool(getattr(self.context, 'display_inline', True))
    
    def set_display_inline(self, value):
        self.context.display_inline = bool(value)
    
    display_inline = property(get_display_inline, set_display_inline)
    
    def get_logo_items(self):
        raw = getattr(self.context, 'logo_items', [])
        logo_items = []
        for x in raw:
            data = x.split('|')
            if data and len(data) == 6:
                logo_items.append(LogoAttrPair(text=data[0], img=data[1], link=data[2], css_class=data[3], new_win=bool(data[4]), separator=data[5]))
        return logo_items

    def set_logo_items(self, value):
        if value is not None:
            self.context.logo_items = ['%s|%s|%s|%s|%s|%s' % (x.logo_text or u'',
                                                           x.logo_img or '',
                                                           x.logo_link or u'',
                                                           x.css_class or u'',
                                                           x.new_win or u'',
                                                           x.separator or u'') for x in value]
        else:
            self.context.logo_items = []

    logo_items = property(get_logo_items, set_logo_items)

    def get_promo_line(self):
        return getattr(self.context, 'promo_line', '')
    
    def set_promo_line(self, value=''):
        self.context.promo_line = value
    
    promo_line = property(get_promo_line, set_promo_line)

logoattr_widget = CustomWidgetFactory(ObjectWidget, LogoAttrPair)
logoitems_widget = CustomWidgetFactory(ListSequenceWidget,
                                        subwidget=logoattr_widget)

class MultiLogoControlPanel(ControlPanelForm):

    form_fields = FormFields(IMultiLogoSchema)
    form_fields['logo_items'].custom_widget = logoitems_widget
    
    label = _("Multi Logo settings")
    description = _("Setup Multi Logo items and options.")
    form_name = _("Multi Logo settings")

