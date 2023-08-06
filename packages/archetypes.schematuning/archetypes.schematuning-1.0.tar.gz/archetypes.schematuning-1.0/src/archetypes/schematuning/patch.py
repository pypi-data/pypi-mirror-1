#
# GNU General Public License (GPL)

__author__ = """Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

from plone.memoize import ram
from zope.interface import directlyProvidedBy
from Products.Archetypes.interfaces import ISchema
from Products.Archetypes.BaseObject import BaseObject
from Acquisition import ImplicitAcquisitionWrapper

import logging
logger = logging.getLogger('archetypes.schematuning')

def cache_key(fun, obj):
    directifaces = directlyProvidedBy(obj).flattened()
    ifaces = [iface.__identifier__ for iface in directifaces]
    return frozenset([obj.__class__.__name__, obj.portal_type] + ifaces)

@ram.cache(cache_key)
def _Schema(self):
    """Return a (wrapped) schema instance for this object instance.
    
    This patch caches it
    """
    schema = ISchema(self)
    return ImplicitAcquisitionWrapper(schema, self)

logger.info('REBINDING Products.Archetypes.BaseObject.Schema')
BaseObject.Schema = _Schema
