from zope import component

from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.Archetypes.tests import attestcase as atc
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer

SiteLayer = layer.PloneSite

configuration = """\
    <configure xmlns="http://namespaces.zope.org/zope">
        <include package="archetypes.schemaextender" />
        <include package="plone.memoize" />
    </configure>
    """

class SchemaTuningLayer(SiteLayer):
    @classmethod
    def setUp(cls):

        PRODUCTS = [
            'plone.memoize',
            'archetypes.schemaextender',
            'archetypes.schematuning',
            ]

        ptc.setupPloneSite(products=PRODUCTS)
        
        fiveconfigure.debug_mode = True
        import archetypes.schemaextender
        zcml.load_config('configure.zcml', archetypes.schemaextender)

        import archetypes.schematuning 
        zcml.load_config('configure.zcml', archetypes.schematuning)

        zcml.load_string(configuration)
        fiveconfigure.debug_mode = False

        component.provideAdapter(instanceSchemaFactory)
        SiteLayer.setUp()


class SchemaTuningTestCase(ptc.PloneTestCase, atc.ATTestCase):
    """We use this base class for all the tests in this package. If necessary,
       we can put common utility or setup code in here.
    """
    layer = SchemaTuningLayer 



