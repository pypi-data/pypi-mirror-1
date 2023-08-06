from zope.component import getUtility
from zope.interface import implements, Interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase
from plone.memoize import view

from Products.CMFPlone.interfaces import IPloneSiteRoot

from collective.multilogo.browser.controlpanel import IMultiLogoSchema

class IMultiLogoViewlet(Interface):
    
    def items():
        """ return all logo items """

class MultiLogoViewlet(ViewletBase):
    implements(IMultiLogoViewlet)
    
    render = ViewPageTemplateFile('multilogo.pt')
    
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return IMultiLogoSchema(portal)

    @view.memoize
    def items(self):
        portal = self.portal_state.portal()
        items = self.prefs.get_logo_items()
        result = []
        for i in items:
            logo = None
            if i.logo_img:
                try:
                    logo = portal.restrictedTraverse(str(i.logo_img)).tag()
                except KeyError:
                    # if logo image not found in the portal
                    pass
            result.append(dict(
                logo_text = logo or i.logo_text,
                logo_link = i.logo_link or self.portal_state.navigation_root_url(),
                css_class = i.css_class or 'multiLogoItem',
                target    = i.new_win and '_blank' or None,
                separator = i.separator or '',
            ))
        return result

    @property
    def inline(self):
        return self.prefs.get_display_inline()

    def update(self):
        super(MultiLogoViewlet, self).update()
        self.promo_line = self.prefs.promo_line