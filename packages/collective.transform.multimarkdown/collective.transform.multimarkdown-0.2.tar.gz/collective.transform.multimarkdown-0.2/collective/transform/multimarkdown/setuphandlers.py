from Products.CMFCore.utils import getToolByName

def registerMimetype(portal):
    """Add text/x-multimarkdown to the mimetype registry"""
    mime_reg = getToolByName(portal, 'mimetypes_registry')
    if not mime_reg.lookup('text/x-multimarkdown'):
        mime_reg.manage_addMimeType(
            "MultiMarkdown",
            ["text/x-multimarkdown"],
            None,
            "text.png"
        )

def uninstallMimetype(portal):
    """Delete the multimarkdown mimetype"""
    mime_reg = getToolByName(portal, 'mimetypes_registry')
    if "text/x-multimarkdown" in mime_reg.objectIds():
        mime_reg.manage_delObjects(["text/x-multimarkdown"])

def installTransform(portal):
    """"""
    transforms = getToolByName(portal, 'portal_transforms')
    if 'multimarkdown_to_html' not in transforms.objectIds():
        transforms.manage_addTransform(
            'multimarkdown_to_html',
            'collective.transform.multimarkdown.multimarkdown_to_html'
        )

def uninstallTransform(portal):
    """"""
    transforms = getToolByName(portal, 'portal_transforms')
    if 'multimarkdown_to_html' in transforms.objectIds():
        transforms.manage_delObjects(['multimarkdown_to_html'])

def importVarious(context):
    """Various import step code"""
    marker_file = 'collective.transform.multimarkdown-default.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = context.getSite()
    registerMimetype(portal)
    installTransform(portal)

def importVariousUninstall(context):
    """Various uninstall step code"""
    marker_file = 'collective.transform.multimarkdown-uninstall.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = context.getSite()
    uninstallMimetype(portal)
    uninstallTransform(portal)
