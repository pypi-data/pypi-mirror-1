from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

from plone.app.memberschema.interfaces import PLUGIN_NAME
from plone.app.memberschema.plugin import manage_addMemberSchemaPropertiesPlugin

def install_plugin(context):
    """Install and prioritize the super group PAS plug-in
    """
    
    if context.readDataFile('plone.app.memberschema_various.txt') is None:
        return
    
    portal = context.getSite()
    
    out = StringIO()
    uf = getToolByName(portal, 'acl_users')

    existing = uf.objectIds()

    if PLUGIN_NAME not in existing:
        manage_addMemberSchemaPropertiesPlugin(uf, PLUGIN_NAME)
        activatePluginInterfaces(portal, PLUGIN_NAME, out)
        print >> out, "%s instaled" % PLUGIN_NAME
    else:
        print >> out, "%s already installed" % PLUGIN_NAME
        
    context.getLogger('plone.app.memberschema').info(out.getvalue())
