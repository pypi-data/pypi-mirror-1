from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite


class RichImageLayer(PloneSite):

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import Products.RichImage
        zcml.load_config("configure.zcml", Products.RichImage)
        fiveconfigure.debug_mode = False
        ztc.installProduct('RichImage', quiet=True)
        ztc.installPackage('plone.app.blob', quiet=True)

    @classmethod
    def tearDown(cls):
        pass

