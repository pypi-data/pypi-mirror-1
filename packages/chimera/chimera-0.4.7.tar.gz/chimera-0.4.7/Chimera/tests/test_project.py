import os, sys
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing                 import ZopeTestCase
from Products.CMFCore.utils  import getToolByName
from Products.CMFPlone.tests import PloneTestCase
from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase

from Products.Chimera.Extensions.Install import install as InstallChimera
ZopeTestCase.installProduct('Chimera')


# This is the test case. You will have to add test_<methods> to your
# class inorder to assert things about your Product.
class ChimeraProjectTest(ArcheSiteTestCase):
    def afterSetUp(self):
        ArcheSiteTestCase.afterSetUp(self)
        InstallChimera(self.portal)
        # Make a temp_folder so that we can aq it
        #self.folder.invokeFactory(type_name="Folder",
        #                          id="temp_folder")


    def test_tool(self):
        assert self.portal.chimera
        ct = self.folder.chimera
        i = ct(u"this is a test", "MS Comic Sans 48")
        assert i.meta_type == "Image"

        assert "Sans" in ct.listFontFamilies()



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChimeraProjectTest))
    return suite

if __name__ == '__main__':
    framework()
