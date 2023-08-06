import unittest

from zope.component import provideAdapter
from zope.component.testing import tearDown

from plone.app.memberschema.interfaces import PLUGIN_NAME

from plone.app.memberschema.plugin import MemberSchemaPropertiesPlugin
from plone.app.memberschema.bag import ZODBBags

from plone.app.memberschema.exportimport.handler import import_schemata, export_schemata
from plone.app.memberschema.exportimport.handler import MemberSchemaPropertiesXMLAdapter

from plone.app.memberschema.tests.common import Basics, Location, Interests, Override

from Products.GenericSetup.tests.common import DummyImportContext
from Products.GenericSetup.tests.common import DummyExportContext

from OFS.ObjectManager import ObjectManager

class ExportImportTest(unittest.TestCase):
    
    def setUp(self):
        
        provideAdapter(ZODBBags)
        provideAdapter(MemberSchemaPropertiesXMLAdapter, name=PLUGIN_NAME)
        
        site = ObjectManager('plone')
        acl_users = ObjectManager('acl_users')
        plugin = MemberSchemaPropertiesPlugin(PLUGIN_NAME)
        
        site._setOb('acl_users', acl_users)
        acl_users._setOb(PLUGIN_NAME, plugin)
        
        plugin.setSchemata([Basics, Location, Interests])
        
        self.site = site
        self.plugin = plugin

    def tearDown(self):
        tearDown()

class TestImport(ExportImportTest):

    def test_empty_import_no_purge(self):
        
        xml = "<memberschema />"
        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        import_schemata(context)
        
        self.assertEquals([Basics, Location, Interests], self.plugin.getSchemata())
    
    def test_add_single_no_purge(self):
        
        xml = "<memberschema><schema>%s</schema></memberschema>" % Override.__identifier__
        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        import_schemata(context)
        
        self.assertEquals([Basics, Location, Interests, Override], self.plugin.getSchemata())

    def test_add_multiple_no_purge(self):
        
        xml = """\
<memberschema>
    <schema>%s</schema>
    <schema>%s</schema>
</memberschema>
""" % (Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Basics, Interests, Location, Override], self.plugin.getSchemata())

    def test_add_multiple_explicit_purge(self):
        
        xml = """\
<memberschema purge="True">
    <schema>%s</schema>
    <schema>%s</schema>
</memberschema>
""" % (Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Location, Override], self.plugin.getSchemata())

    def test_add_multiple_context_purge(self):
        
        xml = """\
<memberschema>
    <schema>%s</schema>
    <schema>%s</schema>
</memberschema>
""" % (Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=True)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Location, Override], self.plugin.getSchemata())

    def test_add_multiple_insert_before_star(self):
        
        xml = """\
<memberschema>
    <schema>%s</schema>
    <schema insert-before="*">%s</schema>
</memberschema>
""" % (Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Override, Basics, Interests, Location], self.plugin.getSchemata())

    def test_add_multiple_insert_after_star(self):
        
        xml = """\
<memberschema>
    <schema insert-after="*">%s</schema>
    <schema>%s</schema>
</memberschema>
""" % (Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        # Note: insert-after="*" is a bit pointless. We always append anyway.
        self.assertEquals([Basics, Interests, Location, Override], self.plugin.getSchemata())

    def test_add_multiple_insert_before_named(self):
        
        xml = """\
<memberschema>
    <schema insert-before="%s">%s</schema>
    <schema>%s</schema>
</memberschema>
""" % (Interests.__identifier__, Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Basics, Location, Interests, Override], self.plugin.getSchemata())

    def test_add_multiple_insert_after_named(self):
        
        xml = """\
<memberschema>
    <schema insert-after="%s">%s</schema>
    <schema>%s</schema>
</memberschema>
""" % (Basics.__identifier__, Location.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Basics, Location, Interests, Override], self.plugin.getSchemata())

    def test_add_multiple_insert_before_named_multiple(self):
        
        xml = """\
<memberschema>
    <schema insert-before="%s">%s</schema>
    <schema insert-before="%s">%s</schema>
</memberschema>
""" % (Interests.__identifier__, Location.__identifier__,
       Interests.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Basics, Location, Override, Interests], self.plugin.getSchemata())

    def test_add_multiple_insert_after_named_multiple(self):
        
        xml = """\
<memberschema>
    <schema insert-after="%s">%s</schema>
    <schema insert-after="%s">%s</schema>
</memberschema>
""" % (Basics.__identifier__, Location.__identifier__,
       Basics.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Basics, Override, Location, Interests], self.plugin.getSchemata())

    def test_add_multiple_insert_after_before_mixed(self):
        
        xml = """\
<memberschema>
    <schema insert-after="%s">%s</schema>
    <schema insert-before="%s">%s</schema>
</memberschema>
""" % (Basics.__identifier__, Location.__identifier__,
       Basics.__identifier__, Override.__identifier__,)

        context = DummyImportContext(self.site, purge=False)
        context._files = {'memberschema.xml': xml}
        
        self.plugin.setSchemata([Basics, Interests])
        
        import_schemata(context)
        
        self.assertEquals([Override, Basics, Location, Interests], self.plugin.getSchemata())

class TestExport(ExportImportTest):
    
    def test_export_multiple(self):
        
        xml = """\
<?xml version="1.0"?>
<memberschema>
 <schema>%s</schema>
 <schema>%s</schema>
</memberschema>
""" % (Basics.__identifier__, Interests.__identifier__)

        context = DummyExportContext(self.site)
        self.plugin.setSchemata([Basics, Interests])
        
        export_schemata(context)
        
        self.assertEquals('memberschema.xml', context._wrote[0][0])
        self.assertEquals(xml, context._wrote[0][1])
    
    def test_export_empty(self):
        
        xml = """\
<?xml version="1.0"?>
<memberschema/>
"""

        context = DummyExportContext(self.site)
        self.plugin.setSchemata([])
        
        export_schemata(context)
        
        self.assertEquals('memberschema.xml', context._wrote[0][0])
        self.assertEquals(xml, context._wrote[0][1])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestImport))
    suite.addTest(unittest.makeSuite(TestExport))
    return suite
