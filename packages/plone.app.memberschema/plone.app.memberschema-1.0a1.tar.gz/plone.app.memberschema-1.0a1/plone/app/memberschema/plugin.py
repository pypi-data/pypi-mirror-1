from zope.interface import implements
from zope.interface.interface import InterfaceClass

from zope import schema

from BTrees.OOBTree import OOBTree

from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet

from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.interfaces.propertysheets import IPropertySheet
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from plone.app.memberschema.interfaces import IBags
from plone.app.memberschema.interfaces import IMemberSchemaPropertiesPlugin

from plone.app.memberschema.utils import resolve, convert_type

_marker = object()

class PropertySheet(object):
    """A mutable property sheet that writes to a persistent bag.
    """
    implements(IPropertySheet, IMutablePropertySheet)

    def __init__(self, id, bag, schema):
        self.__name__ = id
        self.bag = bag
        self.schema = schema

    def getId(self):
        return self._name__
    
    def getPropertyType(self, id):
        return convert_type(self.schema[id])
    
    def hasProperty(self, id):
        return bool(self.schema.get(id))
    
    def propertyIds(self):
        return schema.getFieldNames(self.schema)
    
    def getProperty(self, id, default=_marker):
        value = getattr(self.bag, id, _marker)
        field = self.schema[id]
        if value is _marker and default is _marker:
            value = field.default
        elif value is _marker:
            value = default
        return value

    def propertyItems(self):
        return [(name, self.getProperty(name)) for name in self.propertyIds()]

    def propertyInfo(self, id):
        return dict(id=id,
                    type=self.getPropertyType(id),
                    meta=dict())

    def propertyMap(self):
        return map(self.propertyInfo, self.propertyIds())

    def canWriteProperty(self, user, id):
        return id in self.schema and not self.schema[id].readonly

    def setProperty(self, user, id, value):
        field = self.schema[id].bind(self.bag)
        value = self._forceUnicode(field, value)        
        field.validate(value)
        field.set(self.bag, value)

    def setProperties(self, user, mapping):
        for key, value in mapping.items():
            self.setProperty(user, key, value)
    
    # XXX: This sucks, and is possibly not what we want
    
    def _forceUnicode(self, field, value):
        if field._type == unicode and isinstance(value, str):
            return value.decode('utf-8')
        return value
    
    def _forceUTF8(self, field, value):
        if field._type == str and isinstance(value, unicode):
            return value.encode('utf-8')
        return value

class MemberSchemaPropertiesPlugin(BasePlugin):

    implements(IMemberSchemaPropertiesPlugin, IPropertiesPlugin, IMutablePropertiesPlugin)

    meta_type = "Member Schema Properties Plugin"
    
    _properties = BasePlugin._properties + (
            dict(id='schemata', type='lines', mode='w', label='Schemata'),
        )
    
    schemata = []
    
    def __init__(self, id, title=None):
        self.id = id
        self.title = title
        self._bag_storage = OOBTree() # uid -> Bag

    # IPropertiesPlugin

    def getPropertiesForUser(self, user, request=None):
        bag = self.bags[user.getId()]
        return PropertySheet(self.id, bag, self.getSchema())

    # IMutablePropertiesPlugin

    def setPropertiesForUser(self, user, propertysheet):
        bag = self.bags[user.getId()]
        schema = self.getSchema()
        sheet = PropertySheet(self.id, bag, schema)
        for key, value in propertysheet.propertyItems():
            if key in schema and not schema[key].readonly:
                sheet.setProperty(user, key, value)

    def deleteUser(self, userId):
        del self.bags[userId]
            
    # IMemberSchemaPropertiesPlugin

    def getSchema(self):
        cached = getattr(self, '_v_schema', None)
        schemata = self.getProperty('schemata')
        if cached is None or cached[1] != schemata:
            self._v_schema = cached = (InterfaceClass(name=self.id, bases=self.getSchemata()), schemata,)
        return cached[0]
    
    def getSchemata(self):
        schemata = []
        for schema_name in self.getProperty('schemata'):
            try:
                schemata.append(resolve(schema_name))
            except ImportError:
                pass
        return schemata
    
    def setSchemata(self, schemata):
        self._updateProperty('schemata', [s.__identifier__ for s in schemata])
        
    # Helper methods

    @property
    def bags(self):
        bags = getattr(self, '_v_bags', None)
        if bags is None:
            self._v_bags = bags = IBags(self)
        return bags

manage_addSchemaPropertyPluginForm = PageTemplateFile('browser/plugin', globals())

def manage_addMemberSchemaPropertiesPlugin(self, id, title='', RESPONSE=None ):
    """Add the plugin
    """
    object = MemberSchemaPropertiesPlugin(id, title)
    self._setObject(id, object)

    if RESPONSE:
        RESPONSE.redirect(self.absolute_url() + '/manage_workspace?manage_tabs_message=Member+Schema+Properties+Plugin+created.')
    return object