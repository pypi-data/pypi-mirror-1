from Products.CMFCore.utils import getToolByName

PROPERTIES = [
    {'id':'display_inline','value':'','type':'boolean'},
    {'id':'separator','value':'','type':'string'},
    {'id':'logo_items','value':[],'type':'lines'},
]

def removeConfiglet(self):
    if self.readDataFile('multilogo-uninstall.txt') is None:
        return
    portal_conf=getToolByName(self.getSite(),'portal_controlpanel')
    portal_conf.unregisterConfiglet('PloneAppMultiLogo')

def addProperties(self):
    if self.readDataFile('multilogo.txt') is None:
        return

    site = self.getSite()

    pprop = getToolByName(site, 'portal_properties')

    mprop = pprop.get('logo_properties')
    if not mprop:
        pprop.addPropertySheet('logo_properties', 'Logo Properties')
        mprop = pprop.get('logo_properties')

    for pty in PROPERTIES:
        if not mprop.hasProperty(pty['id']):
            mprop.manage_addProperty(pty['id'], pty['value'], pty['type'])
