import unittest
from Products.CMFCore.utils import getToolByName
from currency.converter.tests.base import CurrencyConverterTestCase
from currency.converter.interfaces import ICurrencyData
from zope.component import queryUtility

class TestSetup(CurrencyConverterTestCase):

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')

## properties.xml

#    def test_currency_data_xml(self):
#        self.failUnless(self.portal.getProperty('currency_data.xml'))

## componentregistry.xml

    def test_utility(self):
        utility = queryUtility(ICurrencyData)
        self.assertNotEquals(None, utility)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
