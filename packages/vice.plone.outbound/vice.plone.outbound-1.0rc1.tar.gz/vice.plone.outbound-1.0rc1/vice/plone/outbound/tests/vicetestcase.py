from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()

class ViceTestCase(PloneTestCase.PloneTestCase):
    pass

class ViceFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    pass

