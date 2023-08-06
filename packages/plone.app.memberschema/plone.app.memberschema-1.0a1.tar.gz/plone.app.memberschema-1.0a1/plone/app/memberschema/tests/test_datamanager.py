import unittest
import zope.component.testing

import os.path
from StringIO import StringIO

from zope.interface import Interface, alsoProvides
from zope.component import provideAdapter, provideUtility, getMultiAdapter
from zope import schema

from z3c.form.interfaces import IDataManager

from plone.app.memberschema.interfaces import PLUGIN_NAME, IPortraitField

from plone.namedfile.interfaces import INamedImage
from plone.namedfile import field
from plone.namedfile.file import NamedImage

from plone.app.memberschema.plugin import MemberSchemaPropertiesPlugin
from plone.app.memberschema.bag import ZODBBags

from plone.app.memberschema.browser.datamanager import MemberDataManager
from plone.app.memberschema.browser.datamanager import MemberPortraitDataManager
from plone.app.memberschema.portrait import NamedFSImage, NamedOFSImage

from plone.app.memberschema.tests.common import zptlogo
from OFS.Image import Image as OFSImage
from Products.CMFCore.FSImage import FSImage

from Products.PlonePAS.plugins.ufactory import PloneUser

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.MembershipTool import MembershipTool

class SimpleData(Interface):

    fullname = schema.TextLine(title=u"Full name", default=u"(no name)")
    email = schema.ASCIILine(title=u"Email")
    readonly = schema.Text(title=u"Readonly", readonly=True)

class Portrait(Interface):

    portrait = field.NamedImage(title=u"Portrait")
    readonly_portrait = field.NamedImage(title=u"Readonly", readonly=True)
    
alsoProvides(Portrait['portrait'], IPortraitField)
alsoProvides(Portrait['readonly_portrait'], IPortraitField)

class FauxMembershipTool(MembershipTool):
    
    portraits = {}
    
    def getPersonalPortrait(self, userid):
        return self.portraits[userid]
    
    def changeMemberPortrait(self, portrait, userid):
        self.portraits[userid] = OFSImage(portrait.filename, portrait.filename, portrait)

class TestMemberDataManager(unittest.TestCase):
    
    def create_user(self, userid):
        user = PloneUser(userid)
        sheet = self.plugin.getPropertiesForUser(user)
        user.addPropertysheet(self.plugin.getId(), sheet)
        return user
        
    def setUp(self):
        
        # Wired in configure.zcml
        provideAdapter(ZODBBags)
        provideAdapter(MemberDataManager)
        provideAdapter(MemberPortraitDataManager)
        
        # Plugin and property sheet
        self.plugin = MemberSchemaPropertiesPlugin(PLUGIN_NAME)
        self.plugin.setSchemata([SimpleData, Portrait])
        
        # Test user
        self.tom = self.create_user('tom')

    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_get_default(self):
        dm = getMultiAdapter((self.tom, SimpleData['fullname'],), IDataManager)
        self.assertEquals(u"(no name)", dm.get())
    
    def test_get_not_in_sheet(self):
        bogus = schema.Text(__name__='bogus', title=u"Bogus")
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertRaises(AttributeError, dm.get)
    
    def test_query_default(self):
        dm = getMultiAdapter((self.tom, SimpleData['fullname'],), IDataManager)
        self.assertEquals(u"(no name)", dm.query())
    
    def test_query_not_in_sheet(self):
        bogus = schema.Text(__name__='bogus', title=u"Bogus")
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertEquals(u"X", dm.query(u"X"))
    
    def test_set_get(self):
        dm = getMultiAdapter((self.tom, SimpleData['fullname'],), IDataManager)
        dm.set(u"Full name")
        self.assertEquals(u"Full name", dm.get())
    
    def test_can_access_normal(self):
        dm = getMultiAdapter((self.tom, SimpleData['fullname'],), IDataManager)
        self.assertEquals(True, dm.canAccess())

    def test_can_access_bogus(self):
        bogus = schema.Text(__name__='bogus', title=u"Bogus")
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertEquals(False, dm.canAccess())

    def test_can_write_normal(self):
        dm = getMultiAdapter((self.tom, SimpleData['fullname'],), IDataManager)
        self.assertEquals(True, dm.canWrite())

    def test_can_write_bogus(self):
        bogus = schema.Text(__name__='bogus', title=u"Bogus")
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertEquals(False, dm.canWrite())

    def test_can_write_readonly(self):
        dm = getMultiAdapter((self.tom, SimpleData['readonly'],), IDataManager)
        self.assertEquals(False, dm.canWrite())

class TestPortraitDataManager(unittest.TestCase):
    
    def create_user(self, userid):
        user = PloneUser(userid)
        sheet = self.plugin.getPropertiesForUser(user)
        user.addPropertysheet(self.plugin.getId(), sheet)
        return user
        
    def setUp(self):
        
        # wired in configure.zcml
        provideAdapter(ZODBBags)
        provideAdapter(MemberDataManager)
        provideAdapter(MemberPortraitDataManager)
        provideAdapter(NamedFSImage, name="portrait")
        provideAdapter(NamedOFSImage, name="portrait")
        
        # fake Plone site with fake membership tool providing fake portraits
        self.site = PloneSite('plone')
        self.site._setOb('portal_membership', FauxMembershipTool('portal_membership'))
        provideUtility(self.site, ISiteRoot)
        
        # plugin and sheets
        self.plugin = MemberSchemaPropertiesPlugin(PLUGIN_NAME)
        self.plugin.setSchemata([SimpleData, Portrait])
        
        # test users with portraits
        self.tom = self.create_user('tom')
        self.dick = self.create_user('dick')
        self.harry = self.create_user('harry')

        self.site.portal_membership.portraits['tom'] = OFSImage('tom.gif', 'Tom', StringIO(zptlogo))
        self.site.portal_membership.portraits['dick'] = FSImage('dick.gif', 
            os.path.join(os.path.dirname(__file__), 'zptlogo.gif'))
        self.site.portal_membership.portraits['harry'] = None

    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_get_ofs(self):
        dm = getMultiAdapter((self.tom, Portrait['portrait'],), IDataManager)
        image = dm.get()
        self.failUnless(INamedImage.providedBy(image))
        self.assertEquals('tom.gif', image.filename)
        self.assertEquals(zptlogo, str(image.data))
    
    def test_get_fsimage(self):
        dm = getMultiAdapter((self.dick, Portrait['portrait'],), IDataManager)
        image = dm.get()
        self.failUnless(INamedImage.providedBy(image))
        self.assertEquals('dick.gif', image.filename)
        self.assertEquals(zptlogo, str(image.data))
    
    def test_get_none(self):
        dm = getMultiAdapter((self.harry, Portrait['portrait'],), IDataManager)
        self.assertRaises(AttributeError, dm.get)
    
    def test_get_not_in_sheet(self):
        bogus = field.NamedImage(__name__='bogus', title=u"Bogus")
        alsoProvides(bogus, IPortraitField)
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertRaises(AttributeError, dm.get)
    
    def test_query_ofs(self):
        dm = getMultiAdapter((self.tom, Portrait['portrait'],), IDataManager)
        image = dm.query('x')
        self.failUnless(INamedImage.providedBy(image))
        self.assertEquals('tom.gif', image.filename)
        self.assertEquals(zptlogo, str(image.data))
    
    def test_query_fsimage(self):
        dm = getMultiAdapter((self.dick, Portrait['portrait'],), IDataManager)
        image = dm.query('x')
        self.failUnless(INamedImage.providedBy(image))
        self.assertEquals('dick.gif', image.filename)
        self.assertEquals(zptlogo, str(image.data))
    
    def test_query_none(self):
        dm = getMultiAdapter((self.harry, Portrait['portrait'],), IDataManager)
        self.assertEquals('x', dm.query('x'))
    
    def test_query_not_in_sheet(self):
        bogus = field.NamedImage(__name__='bogus', title=u"Bogus")
        alsoProvides(bogus, IPortraitField)
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertEquals('x', dm.query('x'))
    
    def test_set_get(self):
        dm = getMultiAdapter((self.dick, Portrait['portrait'],), IDataManager)
        dm.set(NamedImage(data=zptlogo, filename='harry.gif'))
        image = dm.get()
        self.assertEquals('harry.gif', image.filename)
        self.assertEquals(zptlogo, str(image.data))
    
    def test_can_access_normal(self):
        dm = getMultiAdapter((self.dick, Portrait['portrait'],), IDataManager)
        self.assertEquals(True, dm.canAccess())

    def test_can_access_bogus(self):
        bogus = field.NamedImage(__name__='bogus', title=u"Bogus")
        alsoProvides(bogus, IPortraitField)
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertEquals(False, dm.canAccess())

    def test_can_write_normal(self):
        dm = getMultiAdapter((self.dick, Portrait['portrait'],), IDataManager)
        self.assertEquals(True, dm.canWrite())

    def test_can_write_bogus(self):
        bogus = field.NamedImage(__name__='bogus', title=u"Bogus")
        alsoProvides(bogus, IPortraitField)
        dm = getMultiAdapter((self.tom, bogus,), IDataManager)
        self.assertEquals(False, dm.canWrite())

    def test_can_write_readonly(self):
        dm = getMultiAdapter((self.dick, Portrait['readonly_portrait'],), IDataManager)
        self.assertEquals(False, dm.canWrite())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMemberDataManager))
    suite.addTest(unittest.makeSuite(TestPortraitDataManager))
    return suite
