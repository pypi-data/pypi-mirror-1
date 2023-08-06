from persistent import Persistent

from zope.interface import implements
from zope.component import adapts

from plone.app.memberschema.interfaces import IBag, IBags, IMemberSchemaPropertiesPlugin

class Bag(Persistent):
    """Storage for member schemata data
    """
    implements(IBag)

class ZODBBags(object):
    """A factory for bags
    """
    implements(IBags)
    adapts(IMemberSchemaPropertiesPlugin)
    
    def __init__(self, context):
        self.plugin = context
        
    def __getitem__(self, name):
        return self.plugin._bag_storage.setdefault(name, Bag())

    def __delitem__(self, name):
        try:
            del self.plugin._bag_storage[name]
        except KeyError:
            pass