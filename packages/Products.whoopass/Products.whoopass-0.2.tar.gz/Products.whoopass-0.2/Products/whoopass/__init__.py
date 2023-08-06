def initialize(context):
    from Products.whoopass.plugin import WhoPlugin
    from Products.whoopass.plugin import manage_addWhoPluginForm
    from Products.whoopass.plugin import manage_addWhoPlugin

    from Products.PluggableAuthService.PluggableAuthService import \
        registerMultiPlugin

    context.registerClass(WhoPlugin,
                          constructors=(manage_addWhoPluginForm,
                                        manage_addWhoPlugin),
                         )

    registerMultiPlugin(WhoPlugin.meta_type)
