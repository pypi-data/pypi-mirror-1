import unittest

from Products.PloneTestCase.ptc import PloneTestCase
from collective.testcaselayer.ptc import ptc_layer

from zope.component import getMultiAdapter

class CheckPermissionUnit(unittest.TestCase):
    def setUp(self):
        self.operator = pow

    def tearDown(self):
        self.operator = None

    def test_pow(self):
        self.assertEqual(self.operator(2,2), 4)


class CheckIntegration(PloneTestCase):
    layer = ptc_layer

    def test_check_perm(self):
        """ Assert if we can modify a folder """
        view = getMultiAdapter((self.folder, None), name=u"check_permission")
        self.assertTrue(view.check('Modify portal content'))

    def test_check_anonymous(self):
        """ Anonymous cannot modify a folder """
        self.logout()
        view = getMultiAdapter((self.folder, None), name=u"check_permission")
        self.assertFalse(view.check('Modify portal content'))
        

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

