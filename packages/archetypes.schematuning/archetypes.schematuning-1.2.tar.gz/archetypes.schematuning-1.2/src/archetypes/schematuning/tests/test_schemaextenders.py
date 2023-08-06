import unittest

import zope.interface
from zope.component import getGlobalSiteManager

from zope.app.component.hooks import setSite

from five.localsitemanager import make_objectmanager_site

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier

from archetypes.schematuning.patch import cache_key
from archetypes.schematuning.patch import _Schema

from Products.ATContentTypes.interface import IATDocument
from Products.Archetypes import atapi

from base import SchemaTuningTestCase

class ExtensionStringField(ExtensionField, atapi.StringField):
    """ """

class LocalExtender(object):
    """ """
    zope.interface.implements(ISchemaExtender)

    _fields = [
        ExtensionStringField('MyLocalString', widget=atapi.StringWidget()),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields


class GlobalExtender(object):
    """ """
    zope.interface.implements(ISchemaExtender)

    _fields = [
        ExtensionStringField('MyGlobalString', widget=atapi.StringWidget()),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields


class DummyModifier(object):
    """ """
    zope.interface.implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        return 


class TestSchemaExtender(SchemaTuningTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'subsite')

        # Provide the folder 'subsite' with a local objectmanager
        subsite = self.portal._getOb('subsite')
        make_objectmanager_site(subsite)

        # Register a local schema-extender for ATDocument
        sitemanager = subsite.getSiteManager()
        sitemanager.registerAdapter(
                                LocalExtender,
                                (IATDocument,),
                                ISchemaExtender,
                                name='document-local-extender',
                                )

        # Register a global schema-extender for ATDocument
        globalmanager = getGlobalSiteManager()
        globalmanager.registerAdapter(
                                GlobalExtender,
                                (IATDocument,),
                                ISchemaExtender,
                                name='document-global-extender',
                                )

        self.portal.invokeFactory('Document', 'globally-extended-doc')
        subsite.invokeFactory('Document', 'locally-extended-doc')


    def test_local_schema_extension(self):
        """ Test that the schemas of objects with locally registered schema 
            extenders (via a local site-manager) are cached
            separately.
        """
        globally_extended_doc = self.portal._getOb('globally-extended-doc')
        ge_schema = globally_extended_doc.Schema() 
        setSite(globally_extended_doc)
        ge_fields = ge_schema.fields()

        self.assertEquals(
           'MyGlobalString' in [f.__name__ for f in ge_fields],
           True,
        )

        subsite = self.portal._getOb('subsite')
        locally_extended_doc = subsite._getOb('locally-extended-doc')

        # zope.app.component provides an event subscriber for the
        # BeforeTraverseEvent that calls 'setSite'.
        # This is important because it allows 'getAdapter' in
        # zope.app.component.hooks.py to find the local site-manager.
        # Since we are not traversing, we have to call it manually.
        setSite(locally_extended_doc)

        le_schema = locally_extended_doc.Schema()
        le_fields = le_schema.fields()

        # Test that the locally extended document has the extra extended field
        # 'MyLocalString'
        self.assertEquals(
           'MyLocalString' in [f.__name__ for f in le_fields],
           True,
        )

        self.assertEquals(
           'MyGlobalString' in [f.__name__ for f in le_fields],
           True,
        )


    def test_cache_keys(self):
        """ Test that the cache keys for locally and globally extended docs
            differ, but is the same for two global or two local ones.
        """
        subsite = self.portal._getOb('subsite')
        globally_extended_doc = self.portal._getOb('globally-extended-doc')
        locally_extended_doc = subsite._getOb('locally-extended-doc')

        ge_key = cache_key(_Schema, globally_extended_doc)

        setSite(locally_extended_doc)
        le_key = cache_key(_Schema, locally_extended_doc)

        # Test that the cache keys for the locally and globally extended docs
        # differ
        self.assertNotEqual(ge_key, le_key)

        setSite(globally_extended_doc)
        id = self.portal.invokeFactory('Document', 'another-globally-extended-doc')
        another_globally_extended_doc = self.portal._getOb(id)
        age_key = cache_key(_Schema, another_globally_extended_doc)
        
        # Test that the cache keys for two globally extended docs
        # are the same.
        self.assertEquals(ge_key, age_key)

        setSite(locally_extended_doc)
        id = self.portal.invokeFactory('Document', 'another-locally-extended-doc')
        another_locally_extended_doc = self.portal._getOb(id)
        ale_key = cache_key(_Schema, another_locally_extended_doc)
        
        # Test that the cache keys for two locally extended docs
        # are the same.
        self.assertEquals(le_key, ale_key)


    def test_local_schema_modifier(self):
        """ Test that the schemas of objects with locally registered schema 
            modifiers (via a local site-manager) are cached
            separately.
        """
        id = self.portal.invokeFactory('Folder', 'subsite2')
        subsite = self.portal._getOb(id)
        make_objectmanager_site(subsite)

        # Register a local schema for ATDocument
        sitemanager = subsite.getSiteManager()
        sitemanager.registerAdapter(
                                DummyModifier,
                                (IATDocument,),
                                ISchemaModifier,
                                name='document-local-modifier',
                                )

        id = self.portal.invokeFactory('Document', 'unmodified-doc')
        unmodified_doc = self.portal._getOb(id)
        setSite(unmodified_doc)
        um_key = cache_key(_Schema, unmodified_doc)

        id = subsite.invokeFactory('Document', 'locally-modified-doc')
        locally_modified_doc = subsite._getOb(id)
        setSite(locally_modified_doc)
        lm_key = cache_key(_Schema, locally_modified_doc)

        self.assertNotEquals(um_key, lm_key)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchemaExtender))
    return suite

