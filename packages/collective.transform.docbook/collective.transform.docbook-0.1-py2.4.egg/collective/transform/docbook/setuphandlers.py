from Products.CMFCore.utils import getToolByName
#from collective.transform.docbook.mimetype import application_docbook

def registerMimetype(portal):
    """Add application/docbook+xml to the mimetype registry"""
    mime_reg = getToolByName(portal, 'mimetypes_registry')
    if not mime_reg.lookup('application/docbook+xml'):
        #mime_reg.manage_addMimeType(application_docbook)
        mime_reg.manage_addMimeType(
            "DocBook",
            ["application/docbook+xml"],
            None,
            "text.png"
        )

def uninstallMimetype(portal):
    """Delete the docbook mimetype"""
    mime_reg = getToolByName(portal, 'mimetypes_registry')
    if "application/docbook+xml" in mime_reg.objectIds():
        mime_reg.manage_delObjects(["application/docbook+xml"])

def installTransform(portal):
    """"""
    transforms = getToolByName(portal, 'portal_transforms')
    if 'html_to_docbook' not in transforms.objectIds():
        transforms.manage_addTransform(
            'html_to_docbook',
            'collective.transform.docbook.html_to_docbook'
        )

def uninstallTransform(portal):
    """"""
    transforms = getToolByName(portal, 'portal_transforms')
    if 'html_to_docbook' in transforms.objectIds():
        transforms.manage_delObjects(['html_to_docbook'])

def importVarious(context):
    """Various import step code"""
    marker_file = 'collective.transform.docbook-default.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = context.getSite()
    registerMimetype(portal)
    installTransform(portal)

def importVariousUninstall(context):
    """Various uninstall step code"""
    marker_file = 'collective.transform.docbook-uninstall.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = context.getSite()
    uninstallMimetype(portal)
    uninstallTransform(portal)
