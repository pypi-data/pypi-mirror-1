from zope.component import adapts
from zope.component import queryMultiAdapter

from plone.app.memberschema.interfaces import PLUGIN_NAME
from plone.app.memberschema.interfaces import IMemberSchemaPropertiesPlugin

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import XMLAdapterBase

class MemberSchemaPropertiesXMLAdapter(XMLAdapterBase):
    adapts(IMemberSchemaPropertiesPlugin, ISetupEnviron)

    _LOGGER_ID = PLUGIN_NAME

    name = PLUGIN_NAME

    def _importNode(self, node):
        
        if self.environ.shouldPurge():
            self.context.setSchemata([])
        else:
            purge = node.getAttribute('purge')
            if purge.lower() == 'true':
                self.context.setSchemata([])

        schemata = list(self.context.getProperty('schemata'))

        for child in node.childNodes:
            
            if child.nodeName != 'schema':
                continue
        
            child.normalize()
            if len(child.childNodes) != 1 or child.childNodes[0].nodeType != child.TEXT_NODE:
                continue
            
            new_schema = str(child.childNodes[0].data)
        
            insert_before = str(child.getAttribute('insert-before'))
            insert_after = str(child.getAttribute('insert-after'))

            if new_schema in schemata:
                schemata.remove(new_schema)
        
            idx = len(schemata)
        
            relative = insert_before or insert_after
            if relative == '*':
                if insert_before:
                    idx = 0
                elif insert_after:
                    idx = len(schemata)
            elif relative and relative in schemata:
                idx = schemata.index(relative)
                if insert_after:
                    idx += 1
        
            schemata.insert(idx, new_schema)
        
        self.context._updateProperty('schemata', schemata)

    def _exportNode(self):
        node = self._doc.createElement('memberschema')
        
        for schema in self.context.getSchemata():
            child = self._doc.createElement('schema')
            text = self._doc.createTextNode(schema.__identifier__)
            child.appendChild(text)
            node.appendChild(child)

        return node


def import_schemata(context):
    
    logger = context.getLogger(PLUGIN_NAME)
    acl_users = getToolByName(context.getSite(), 'acl_users')
    plugin = getattr(acl_users, PLUGIN_NAME, None)
    
    if plugin is None or not IMemberSchemaPropertiesPlugin.providedBy(plugin):
        logger.info("Cannot find member schema properties plugin %s" % PLUGIN_NAME)
        return

    importer = queryMultiAdapter((plugin, context), IBody, name=PLUGIN_NAME)
    if importer:
        body = context.readDataFile('memberschema.xml')
        if body is not None:
            importer.body = body
    
def export_schemata(context):

    logger = context.getLogger(PLUGIN_NAME)
    acl_users = getToolByName(context.getSite(), 'acl_users')
    plugin = getattr(acl_users, PLUGIN_NAME, None)
    
    if plugin is None or not IMemberSchemaPropertiesPlugin.providedBy(plugin):
        logger.info("Cannot find member schema properties plugin %s" % PLUGIN_NAME)
        return

    exporter = queryMultiAdapter((plugin, context), IBody, name=PLUGIN_NAME)
    if exporter:
        body = exporter.body
        if body is not None:
            context.writeDataFile('memberschema.xml', body, exporter.mime_type)