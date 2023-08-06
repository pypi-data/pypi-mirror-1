from Products.CMFCore.utils import getToolByName

transform = 'avi_to_flv'

def installTransform(portal):
    """
    Install avi2flv transform.
    """
    transforms = getToolByName(portal, 'portal_transforms')
    if transform not in transforms.objectIds():
        transforms.manage_addTransform(
            transform,
            'stxnext.transform.avi2flv.%s' % transform,
        )

def uninstallTransform(portal):
    """
    Uninstall avi2flv transform.
    """
    transforms = getToolByName(portal, 'portal_transforms')
    if transform in transforms.objectIds():
        transforms.manage_delObjects([transform])

def importVarious(context):
    """
    Various import step code.
    """
    marker_file = 'stxnext.transform.avi2flv.txt'
    if context.readDataFile(marker_file) is None:
        ## don't install if called as dependency
        return
    portal = context.getSite()
    installTransform(portal)

def importVariousUninstall(context):
    """
    Various uninstall step code.
    """
    marker_file = 'stxnext.transform.avi2flv-uninstall.txt'
    if context.readDataFile(marker_file) is None:
        ## don't uninstall if called as dependency
        return
    portal = context.getSite()
    uninstallTransform(portal)
