from Products.CMFCore.utils import getToolByName

def registerMimetype(portal):
    """Add text/wiki+creole to the mimetype registry"""
    mime_reg = getToolByName(portal, 'mimetypes_registry')
    if not mime_reg.lookup('text/wiki+creole'):
        mime_reg.manage_addMimeType(
            "Creole Wiki Text",
            ["text/wiki+creole"],
            None,
            "text.png"
        )

def uninstallMimetype(portal):
    """Delete the creole mimetype"""
    mime_reg = getToolByName(portal, 'mimetypes_registry')
    if "text/wiki+creole" in mime_reg.objectIds():
        mime_reg.manage_delObjects(["text/wiki+creole"])

def installTransform(portal):
    """"""
    transforms = getToolByName(portal, 'portal_transforms')
    if 'creole_to_html' not in transforms.objectIds():
        transforms.manage_addTransform(
            'creole_to_html',
            'collective.transform.creole.creole_to_html'
        )

def uninstallTransform(portal):
    """"""
    transforms = getToolByName(portal, 'portal_transforms')
    if 'creole_to_html' in transforms.objectIds():
        transforms.manage_delObjects(['creole_to_html'])

def importVarious(context):
    """Various import step code"""
    marker_file = 'collective.transform.creole-default.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = context.getSite()
    registerMimetype(portal)
    installTransform(portal)

def importVariousUninstall(context):
    """Various uninstall step code"""
    marker_file = 'collective.transform.creole-uninstall.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = context.getSite()
    uninstallMimetype(portal)
    uninstallTransform(portal)
