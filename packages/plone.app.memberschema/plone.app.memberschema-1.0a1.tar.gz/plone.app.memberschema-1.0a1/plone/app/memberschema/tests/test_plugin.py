import unittest
from datetime import date

from zope.component import provideAdapter

import zope.component.testing

from zope import schema

from plone.app.memberschema.interfaces import PLUGIN_NAME

from plone.app.memberschema.plugin import MemberSchemaPropertiesPlugin
from plone.app.memberschema.bag import ZODBBags

from plone.app.memberschema.tests.common import Basics, Location, Interests, Override

class FauxUser(object):
    
    def __init__(self, id):
        self.id = id
        
    def getId(self):
        return self.id

class TestPlugin(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(ZODBBags)
        
        self.plugin = MemberSchemaPropertiesPlugin(PLUGIN_NAME)
        self.plugin.setSchemata([Basics, Location, Interests])
        
        self.tom = FauxUser('tom')
        self.dick = FauxUser('dick')
        self.harry = FauxUser('harry')

    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_hasProperty(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        self.assertEquals(True, properties.hasProperty('first_name'))
        self.assertEquals(False, properties.hasProperty('foobar'))
    
    def test_getPropertyType(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
    
        self.assertEquals('string', properties.getPropertyType('first_name'))
        self.assertEquals('string', properties.getPropertyType('employee_number'))
        self.assertEquals('string', properties.getPropertyType('address'))
        self.assertEquals('date', properties.getPropertyType('birthday'))
        self.assertEquals('int', properties.getPropertyType('number_of_pets'))
        self.assertEquals(None, properties.getPropertyType('randomly_readonly'))
    
    def test_propertyIds(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        self.assertEquals(['first_name', 'birthday', 'surname', 'address',
                           'number_of_pets', 'employee_number', 'randomly_readonly'],
                           properties.propertyIds())
    
    def test_getProperyDefault(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        self.assertEquals(None, properties.getProperty('first_name'))
        self.assertEquals(3, properties.getProperty('number_of_pets'))
    
    def test_propertyItemsDefault(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        self.assertEquals([('first_name', None), ('birthday', None), ('surname', None),
                           ('address', None), ('number_of_pets', 3), ('employee_number', None),
                           ('randomly_readonly', {1: 1, 2: 2})],
                          properties.propertyItems())
    
    def test_propertyMap(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        self.assertEquals([{'meta': {}, 'type': 'string', 'id': 'first_name'},
                           {'meta': {}, 'type': 'date', 'id': 'birthday'},
                           {'meta': {}, 'type': 'string', 'id': 'surname'},
                           {'meta': {}, 'type': 'string', 'id': 'address'},
                           {'meta': {}, 'type': 'int', 'id': 'number_of_pets'},
                           {'meta': {}, 'type': 'string', 'id': 'employee_number'},
                           {'meta': {}, 'type': None, 'id': 'randomly_readonly'}],
                          properties.propertyMap())
    
    def test_canWrite(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        self.assertEquals(True, properties.canWriteProperty(self.tom, 'first_name'))
        self.assertEquals(False, properties.canWriteProperty(self.tom, 'foobar'))
        self.assertEquals(False, properties.canWriteProperty(self.tom, 'random_readonly'))

    def test_setPropertyPersists(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        self.assertEquals(None, properties.getProperty('first_name'))
        
        properties.setProperty(self.tom, 'first_name', u'Tom')
        properties = self.plugin.getPropertiesForUser(self.tom)
        self.assertEquals(u'Tom', properties.getProperty('first_name'))
        
        properties = self.plugin.getPropertiesForUser(self.dick)
        self.assertEquals(None, properties.getProperty('first_name'))
    
    def test_setPropertyValidates(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        try:
            properties.setProperty(self.tom, 'first_name', 123)
        except schema.ValidationError:
            pass
        else:
            self.fail()
        
    def test_setProperties(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        properties.setProperties(self.tom, {'first_name': u'Tom', 'surname': u'Tomson'})
        self.assertEquals(u"Tom", properties.getProperty('first_name'))
        self.assertEquals(u"Tomson", properties.getProperty('surname'))
    
    def test_setPropertiesForUser(self):
        properties = self.plugin.getPropertiesForUser(self.tom)
        
        properties.setProperties(self.tom, {'first_name': u'Tom', 'surname': u'Tomson',
                                            'employee_number': 'A1234',
                                            'number_of_pets': 2,
                                            'address': u"Number one\nThe screen.",
                                            'birthday': date(2001, 1, 1)})
        
        self.plugin.setPropertiesForUser(self.dick, properties)
        properties = self.plugin.getPropertiesForUser(self.dick)
        self.assertEquals(u'Tom', properties.getProperty('first_name'))
        self.assertEquals(2, properties.getProperty('number_of_pets'))
        
    def test_deleteUser(self):
        properties = self.plugin.getPropertiesForUser(self.harry)
        properties.setProperties(self.harry, {'first_name': u'Harry'})
        self.assertEquals(u'Harry', properties.getProperty('first_name'))
        
        self.plugin.deleteUser(self.harry.getId())
        
        properties = self.plugin.getPropertiesForUser(self.harry)
        self.assertEquals(None, properties.getProperty('first_name'))
        
    def test_getSchema(self):
        schema = self.plugin.getSchema()
        self.assertEquals('plone.app.memberschema.plugin.schema_properties',
                          schema.__identifier__)
                          
        self.failUnless(schema['first_name'] is     Basics['first_name'])
        
        # earlier schemata win over later ones
        self.failUnless(schema['birthday']   is     Interests['birthday'])
        self.failUnless(schema['birthday']   is not Override['birthday'])
        
    def test_getSchemata(self):
        self.assertEquals([Basics, Location, Interests], self.plugin.getSchemata())
        
    def test_setSchemata(self):
        self.plugin.setSchemata([Basics, Override])
        schema = self.plugin.getSchema()
        
        self.failUnless(schema['first_name'] is     Basics['first_name'])
        self.failUnless(schema['birthday']   is not Interests['birthday'])
        self.failUnless(schema['birthday']   is     Override['birthday'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPlugin))
    return suite
