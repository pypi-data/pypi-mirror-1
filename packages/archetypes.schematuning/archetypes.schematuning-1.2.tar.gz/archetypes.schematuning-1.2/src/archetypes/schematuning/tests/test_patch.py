import unittest

from archetypes.schematuning.patch import cache_key
from archetypes.schematuning.patch import _Schema

from base import SchemaTuningTestCase

class TestPatch(SchemaTuningTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()

    def test_cache_keys(self):
        """ Test that the cache keys for two docs are the same.
        """
        id = self.portal.invokeFactory('Document', 'doc1')
        doc1 = self.portal._getOb(id)
        self.portal.invokeFactory('Document', 'do2c')
        doc2 = self.portal._getOb(id)

        key1 = cache_key(_Schema, doc1)
        key2 = cache_key(_Schema, doc2)

        self.assertEquals(key1, key2)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPatch))
    return suite

