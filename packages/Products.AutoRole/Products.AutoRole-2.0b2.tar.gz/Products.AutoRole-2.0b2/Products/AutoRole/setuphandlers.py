from StringIO import StringIO
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces


def setup_auto_role_plugin(portal):
    uf = portal.acl_users
    ids = uf.objectIds()
    out = StringIO()

    AutoRole = uf.manage_addProduct['AutoRole']

    if 'auto_role' not in ids:
        AutoRole.addAutoRole('auto_role', 'Automatic Role Provider')
        activatePluginInterfaces(portal, 'auto_role', out,
                                 disable=['IGroupsPlugin'])


def importVarious(context):
    site = context.getSite()
    logger = context.getLogger('autorole')

    if context.readDataFile('autorole.txt') is None:
        logger.info('Nothing to import.')
        return

    setup_auto_role_plugin(site)
    logger.info('PAS plugin imported.')
