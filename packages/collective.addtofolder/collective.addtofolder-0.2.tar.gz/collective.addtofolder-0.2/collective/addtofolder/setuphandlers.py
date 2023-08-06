from collective.addtofolder.interfaces import IAddMenuConfiguration
from collective.addtofolder.configlet import AddMenuConfiguration
#from Products.CMFCore.utils import getToolByName

def isNotAddToFolderProfile(context):
    return context.readDataFile("addtofolder_marker.txt") is None

def setup_site(context):
    if isNotAddToFolderProfile(context):
        return

    site = context.getSite()
    sm = site.getSiteManager()

    if not sm.queryUtility(IAddMenuConfiguration, name='addmenuconfig'):
        sm.registerUtility(
                        AddMenuConfiguration(),
                        IAddMenuConfiguration,
                        'addmenuconfig')
