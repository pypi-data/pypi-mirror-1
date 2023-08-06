
def setup_auto_role_plugin(portal):
    uf = portal.acl_users
    ids = uf.objectIds()

    if 'auto_role' not in ids:
        factory = uf.manage_addProduct['AutoRole']
        factory.addAutoRole('auto_role', 'Automatic Role Provider')

        plugin = uf['auto_role']
        plugin.manage_activateInterfaces(['IExtractionPlugin',
                                          'IAuthenticationPlugin',
                                          'IRolesPlugin'])


def importVarious(context):
    site = context.getSite()
    logger = context.getLogger('autorole')

    if context.readDataFile('autorole.txt') is None:
        logger.info('Nothing to import.')
        return

    setup_auto_role_plugin(site)
    logger.info('PAS plugin imported.')
