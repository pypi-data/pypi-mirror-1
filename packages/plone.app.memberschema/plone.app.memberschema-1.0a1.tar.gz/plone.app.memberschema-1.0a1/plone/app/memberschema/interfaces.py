from zope.interface import Interface

from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin

from plone.namedfile.interfaces import INamedField

PLUGIN_NAME = "schema_properties"

class IBag(Interface):
    """Storage for the properties of a single user
    """
    
    def __getattr__(name):
        """Get the value for the given property
        """
        
    def __setattr__(name):
        """Set the value for the given property
        """

class IBags(Interface):
    """Storage for bags. Register an adapter from
    IMemberSchemaPropertiesPlugin to this interface to overide the storage
    mechanism (e.g. to support SQL or LDAP storage).
    """
    
    def __getitem__(id):
        """Get a the bag for the given user. This should never fail.
        """
        
    def __delitem__(id):
        """Delete the bag for the given user. Should not fail if the name
        cannot be found.
        """

class IMemberSchemaPropertiesPlugin(IMutablePropertiesPlugin, IPropertiesPlugin):
    """Propeties plugin that can be based on one or more schemata
    """
    
    def getSchema():
        """Return a single schema representing fields from all member schemata
        """
    
    def getSchemata():
        """Return a list of schemata used as member properties
        """
    
    def setSchemata(schemata):
        """Set the list of member schemata
        """

class IPortraitField(INamedField):
    """Marker interface for an image field that can be used to store
    portraits. Should be used for a plone.namedfile field.
    """
