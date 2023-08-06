from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

from borg.supergroup.config import PLUGIN_NAME
from borg.supergroup.plugin import manage_addSuperGroupProvider

def install_plugin(context):
    """Install and prioritize the super group PAS plug-in
    """
    
    if context.readDataFile('borg.supergroup_various.txt') is None:
        return
    
    portal = context.getSite()
    
    out = StringIO()
    uf = getToolByName(portal, 'acl_users')

    existing = uf.objectIds()

    if PLUGIN_NAME not in existing:
        manage_addSuperGroupProvider(uf, PLUGIN_NAME)
        activatePluginInterfaces(portal, PLUGIN_NAME, out)
    else:
        print >> out, "%s already installed" % PLUGIN_NAME
        
    context.getLogger('borg.supergroup').info(out.getvalue())
