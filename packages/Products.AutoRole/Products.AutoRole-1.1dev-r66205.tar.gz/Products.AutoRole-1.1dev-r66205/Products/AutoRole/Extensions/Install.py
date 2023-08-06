from StringIO import StringIO

from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

def setupPlugins(portal, out):
    uf = portal.acl_users
    ids = uf.objectIds()

    print >> out, "\nPlugin setup"

    AutoRole = uf.manage_addProduct['AutoRole']

    if 'AutoRole' not in ids:
        AutoRole.addAutoRole('AutoRole')
        print >> out, "Added AutoRole plugin."
        activatePluginInterfaces(portal, 'AutoRole', out)

        plugins = portal.acl_users.plugins
        #plist = plugins.listPlugins(IUserFactoryPlugin)

        # Move plugins all the way to the top...
        #while plugins.listPlugins(IRolesPlugin)[0][0] != 'AutoRole':
        #    plugins.movePluginsUp(IRolesPlugin, ['AutoRole'])


def install(self):
    out = StringIO()

    setupPlugins(self, out)

    return out.getvalue()
