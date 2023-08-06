#
# GNU General Public License (GPL)

__author__ = """Jens Klein <jens@bluedynamics.com>, Hedley Roos <hedley@upfrontsystems.co.za>"""
__docformat__ = 'plaintext'

import logging

from zope.interface import directlyProvidedBy
from zope.component import getAdapters
from Acquisition import ImplicitAcquisitionWrapper

from plone.memoize import ram
from Products.Archetypes.interfaces import ISchema
from Products.Archetypes.BaseObject import BaseObject
try:
    from archetypes.schemaextender.interfaces import \
        ISchemaExtender, IBrowserLayerAwareExtender, ISchemaModifier
    HAS_SCHEMA_EXTENDER = True
except ImportError:
    HAS_SCHEMA_EXTENDER = False

def cache_key(fun, obj):
    # Determine if any browser layer aware schema extenders
    # exist for this object. If there are any they need to be
    # part of the key.
    layers = []
    adapters = []
    if HAS_SCHEMA_EXTENDER:
        for name, adapter in getAdapters((obj,), ISchemaExtender):
            adapters.append(name)
            if IBrowserLayerAwareExtender.providedBy(adapter):
                layers.append(adapter.layer)

        for name, adapter in getAdapters((obj,), ISchemaModifier):
            adapters.append(name)

    directifaces = directlyProvidedBy(obj).flattened()
    ifaces = [iface.__identifier__ for iface in directifaces]
    return frozenset([obj.__class__.__name__, obj.portal_type] + ifaces 
        + layers + adapters + [id(obj.__class__)])


@ram.cache(cache_key)
def _Schema(self):
   """This patch caches the unwrapped schema
   """
   schema = ISchema(self)
   return schema

def Schema(self, use_cache=True):
       """Return a (wrapped) schema instance for this object instance.
       """
       if use_cache:
           schema = self._Schema()
       else:
           schema = ISchema(self)
       return ImplicitAcquisitionWrapper(schema, self)

def invalidateSchema(self):
    """Any code that changes the schema at runtime must call this
    method to clear the old schema from the cache.
    """
    ram.choose_cache('archetypes.schematuning.patch._Schema').ramcache.invalidateAll()
    # todo: figure out why line below is not working as expected
    #ram.choose_cache('archetypes.schematuning.patch._Schema').ramcache.invalidate(cache_key(None, self))

def _isSchemaCurrent(self):
    """Determines whether the current object's schema is up to date.
    """
    return self._signature == self.Schema(use_cache=False).signature()

def _updateSchema(self, excluded_fields=[], out=None,
                      remove_instance_schemas=False):
    self.invalidateSchema()
    result = self._old_updateSchema(excluded_fields, out, remove_instance_schemas)
    self.invalidateSchema()
    return result

logger = logging.getLogger('archetypes.schematuning')
logger.info('REBINDING Products.Archetypes.BaseObject.Schema')
BaseObject._Schema = _Schema
BaseObject.Schema = Schema
BaseObject.invalidateSchema = invalidateSchema
BaseObject._isSchemaCurrent = _isSchemaCurrent
BaseObject._old_updateSchema = BaseObject._updateSchema
BaseObject._updateSchema = _updateSchema
