from base import TestCase
from config import NT_PROPERTIES, S_PROPERTIES

class TestPropertiesToolConf(TestCase):

    def afterSetUp(self):
        self.ptool = self.portal.portal_properties

    def testConfigurationNavtreePropertiesTool(self):
        # Configuration navtree_properties
        props = self.ptool.navtree_properties
        for prop_id, prop_type, prop_value in NT_PROPERTIES:
           self.assertTrue(prop_id in props.propertyIds())
           self.assertEqual(props.getPropertyType(prop_id), prop_type)
           p_value = list(props.getProperty(prop_id))
           prop_value.sort()
           p_value.sort()
           self.assertEqual([v for v in prop_value if v in p_value], prop_value)

    def testConfigurationSitePropertiesTool(self):
        # Configuration site_properties
        props = self.ptool.site_properties
        for prop_id, prop_type, prop_value in S_PROPERTIES:
           self.assertTrue(prop_id in props.propertyIds())
           self.assertEqual(props.getPropertyType(prop_id), prop_type)
           p_value = list(props.getProperty(prop_id))
           prop_value.sort()
           p_value.sort()
           self.assertEqual([v for v in prop_value if v in p_value], prop_value)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPropertiesToolConf))
    return suite

