from Products.PluggableAuthService import registerMultiPlugin
from AccessControl.Permissions import add_user_folders

from borg.supergroup import plugin

registerMultiPlugin(plugin.SuperGroupProvider.meta_type)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    # Register PAS plug-in
    
    context.registerClass(plugin.SuperGroupProvider,
                          permission = add_user_folders,
                          constructors = (plugin.manage_addSuperGroupProviderForm,
                                          plugin.manage_addSuperGroupProvider),
                          visibility = None)
