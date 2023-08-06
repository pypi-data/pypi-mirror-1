def initialize(context):
    from AccessControl.Permissions import manage_users
    from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
    from pas.plugins.adpwchange import plugin
    
    registerMultiPlugin(plugin.ADPasswordChangePlugin.meta_type)
    context.registerClass(plugin.ADPasswordChangePlugin,
            permission=manage_users,
            constructors=(plugin.manage_addADPasswordChangePlugin,
                          plugin.addADPasswordChangePlugin),
            visibility=None)

    
