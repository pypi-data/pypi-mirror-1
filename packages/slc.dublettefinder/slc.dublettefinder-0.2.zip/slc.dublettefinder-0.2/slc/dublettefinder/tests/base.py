from Testing import ZopeTestCase as ztc

from zope import component

from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer 

from plone import browserlayer

from slc.dublettefinder.interfaces import IDubletteFinderLayer

SiteLayer = layer.PloneSite

class DubletteFinderLayer(SiteLayer):

    @classmethod
    def setUp(cls):
        """ Set up the additional products required for the 
            DubletteFinder.
        """
        PRODUCTS = [
            'slc.dublettefinder',
            ]
        ptc.setupPloneSite(products=PRODUCTS)

        fiveconfigure.debug_mode = True
        import slc.dublettefinder
        zcml.load_config('configure.zcml', slc.dublettefinder)
        fiveconfigure.debug_mode = False
        
        ztc.installPackage('slc.dublettefinder')

        browserlayer.utils.register_layer(
                                IDubletteFinderLayer, 
                                name='slc.dublettefinder'
                                )

        component.provideAdapter(instanceSchemaFactory)
        SiteLayer.setUp()
    

class DubletteFinderTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    layer = DubletteFinderLayer

