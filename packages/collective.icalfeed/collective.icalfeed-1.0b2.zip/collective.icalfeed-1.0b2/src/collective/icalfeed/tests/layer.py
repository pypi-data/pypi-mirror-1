from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite


class TestLayer(PloneSite):
    """ layer for integration tests """

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import collective.icalfeed
        zcml.load_config('configure.zcml', collective.icalfeed)
        fiveconfigure.debug_mode = False

    @classmethod
    def tearDown(cls):
        pass

