from Products.CMFCore.utils import getToolByName

product_name = 'Products.CMFSquidTool'

def install(self, reinstall=False):
    portal_setup = getToolByName(self, 'portal_setup')
    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    try:
        portal_setup.runAllImportStepsFromProfile('profile-%s:default' % product_name, purge_old=False)
    except AttributeError:
        # old style for Plone 2.5 compatibility
        portal_setup.setImportContext('profile-%s:default' % product_name)
        portal_setup.runAllImportSteps(purge_old=False)
    portal_quickinstaller.notifyInstalled(product_name)

