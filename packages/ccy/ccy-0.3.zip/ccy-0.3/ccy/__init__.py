import os
import sys
 
VERSION = (0, 3)
 
def get_version():
    if len(VERSION) == 3:
        try:
            int(VERSION[2])
            v  = '%s.%s.%s' % VERSION
        except:
            v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v
 
__version__ = get_version()


from core import currency as _currency

from data.currency import make_ccys
_currency.ccydb.load = make_ccys

from core.currency import currencydb, currency, ccypair, ccypairsdb
from core.country import country, countryccy, set_new_country, \
                         countries, set_country_map, country_map, \
                         CountryError

# Shortcuts
cross     = lambda code : currency(code).as_cross()
crossover = lambda code : currency(code).as_cross('/')