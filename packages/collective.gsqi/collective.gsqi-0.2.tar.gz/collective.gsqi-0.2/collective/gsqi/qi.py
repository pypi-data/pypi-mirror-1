from Products.CMFQuickInstallerTool import InstalledProduct

def uninstall(
    self, cascade=InstalledProduct.InstalledProduct.default_cascade,
    reinstall=False, REQUEST=None):
    """Don't do removal on reinstall"""
    portal = self.portal_url.getPortalObject() 

    # TODO eventually we will land Event system and could remove
    # this 'removal_inprogress' hack
    if self.isLocked() and getattr(portal, 'removal_inprogress', False):
        raise ValueError, 'The product is locked and cannot be uninstalled!'

    res=''
    afterRes=''

    uninstaller = self.getUninstallMethod()
    beforeUninstall = self.getBeforeUninstallMethod()

    if uninstaller:
        uninstaller = uninstaller.__of__(portal)
        try:
            res=uninstaller(portal, reinstall=reinstall)
            # XXX log it
        except TypeError:
            res=uninstaller(portal)

    if beforeUninstall:
        beforeUninstall = beforeUninstall.__of__(portal)
        beforeRes, cascade = beforeUninstall(portal, reinstall=reinstall,
                                            product=self, cascade=cascade)

    if not reinstall:
        self._cascadeRemove(cascade)

    self.status='uninstalled'
    self.log('uninstalled\n'+str(res)+str(afterRes))

    if REQUEST and REQUEST.get('nextUrl',None):
        return REQUEST.RESPONSE.redirect(REQUEST['nextUrl'])
