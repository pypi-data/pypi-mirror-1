from data import *

from unittest import TestCase


class CcyTest(TestCase):
        
    def testdefaultcountry(self):
        ccys = currencydb()
        for ccy in ccys.values():
            self.assertEqual(ccy.code[:2],ccy.default_country)
            
    def testiso(self):
        ccys = currencydb()
        iso = {}
        for ccy in ccys.values():
            self.assertFalse(iso.has_key(ccy.isonumber))
            iso[ccy.isonumber] = ccy
            
    def test2letters(self):
        ccys = currencydb()
        twol = {}
        for ccy in ccys.values():
            self.assertFalse(twol.has_key(ccy.twolettercode))
            twol[ccy.twolettercode] = ccy
    
        