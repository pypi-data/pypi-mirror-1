#
# ATBiblioStyles tests
#

from Products.ATBiblioStyles.tests import BibliostylesTestCase
import constants

class TestSetup(BibliostylesTestCase.BibliostylesTestCase):

    def testSkins(self):
        portal_skins = self.portal.portal_skins.objectIds()
        for skin in constants.FSDIRECTORYVIEWS:
            self.failUnless(skin in portal_skins)

    def testSkinLayers(self):
        skin_paths = self.portal.portal_skins.getSkinPaths()
        for layer in constants.FSDIRECTORYVIEWS:
            for skin_path in [s[1] for s in skin_paths]:
                self.failUnless(layer in skin_path)

    def testTools(self):
        portalcontents = self.portal.objectIds()
        for tool_name in constants.TOOLNAMES:
            self.failUnless(tool_name in portalcontents)

    def testStyles(self):
        tool = self.portal.portal_bibliostyles
        toolstyles = tool.objectIds()
        for style in constants.BIBREFSTYLES:
            self.failUnless(style in toolstyles)

    def testPortalTypes(self):
        portal_types = self.portal.portal_types.objectIds()
        for content_type in constants.CONTENTTYPES:
            self.failUnless(content_type in portal_types)

    def testPortalFactorySetup(self):
        factoryTypes = self.portal.portal_factory.getFactoryTypes().keys()
        for t in constants.CONTENTTYPES:
            self.failUnless(t in factoryTypes)

    def testFolderishTypes(self):
        sp = self.portal.portal_properties.site_properties
        for ft in constants.FOLDERISHTYPES:
            self.failUnless(ft in sp.use_folder_tabs)
            self.failUnless(ft in sp.typesLinkToFolderContentsInFC)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
