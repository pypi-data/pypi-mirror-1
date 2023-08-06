# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_service.py 28983 2008-06-04 10:18:12Z sylvain $


from Products.Five import zcml
from Products import Five
zcml.load_config('meta.zcml', Five)
zcml.load_config('configure.zcml', Five)
# Now it seems that SilvaTestCase try to do smart installPackage, but
# fails since we need to load GenericSetup before. So this code should
# endup before the import of SilvaTestCase
from Products import GenericSetup
zcml.load_config('meta.zcml', GenericSetup)
zcml.load_config('configure.zcml', GenericSetup)

from Products.Silva.tests import SilvaTestCase

from Testing import ZopeTestCase as ztc


class CaptchaTestCase(SilvaTestCase.SilvaTestCase):
    """Test case for captcha integration.
    """


    def afterSetUp(self):
        """After set up, install the extension.
        """
        root = self.getRoot()
        root.service_extensions.install('silva.captcha')

    def test_00install(self):
        """Install should change the members services and set up an
        acl_user.
        """
        root = self.getRoot()

        # First the extension should be installed
        service_extensions = root.service_extensions
        self.failUnless(service_extensions.is_installed('silva.captcha'))


    def test_20uninstall(self):
        """Uninstall should work.
        """
        root = self.getRoot()
        root.service_extensions.uninstall('silva.captcha')
        self.failIf(root.service_extensions.is_installed('silva.captcha'))



import unittest
def test_suite():

    # Load the Zope Product
    ztc.installProduct('GenericSetup')
    ztc.installPackage('silva.captcha')

    # Load our ZCML, which add the extension as a Product
    from silva import captcha
    zcml.load_config('configure.zcml', captcha)

    # Run tests
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CaptchaTestCase))
    return suite
