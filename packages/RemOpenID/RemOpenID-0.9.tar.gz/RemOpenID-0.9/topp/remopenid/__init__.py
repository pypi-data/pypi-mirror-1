from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from plone.openid import config

if config.HAS_OPENID and config.HAS_SSL:
    import plugin
    registerMultiPlugin(plugin.RemOpenIdPlugin.meta_type)
    
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    if config.HAS_OPENID:
        context.registerClass(plugin.RemOpenIdPlugin,
                              permission=ManageUsers,
                              constructors=(plugin.manage_addRemOpenIdPlugin,
                                            plugin.addRemOpenIdPlugin),
                              visibility=None,
                              icon="www/openid.png",
                              )
