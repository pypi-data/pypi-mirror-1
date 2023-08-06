

__all__ = ['currency','ccypair','currencydb','ccypairsdb','currencypair']

usd_order = 5


def overusdfun(v1):
    return v1
def overusdfuni(v1):
    return 1./v1



class ccy(object):
    '''
    Currency object
    '''
    def __init__(self, code, isonumber, twolettercode, order, name, 
                 roundoff  = 4,
                 default_country = None,
                 fixeddc   = None,
                 floatdc   = None,
                 fixedfreq = None,
                 floatfreq = None,
                 future    = None):
        #from qmpy.finance.dates import get_daycount
        self.code          = str(code)
        self.id            = self.code
        self.isonumber     = isonumber
        self.twolettercode = str(twolettercode)
        self.order         = int(order)
        self.name          = str(name)
        self.raundoff      = roundoff
        self.default_country = default_country
        #self.fixeddc       = get_daycount(fixeddc)    
        #self.floatdc       = get_daycount(floatdc)
        #self.fixedfreq     = str(fixedfreq)
        #self.floatfreq     = str(floatfreq)
        self.future        = ''
        if future:
            self.future    = str(future)
            
    def description(self):
        if self.order > usd_order:
            v = 'USD / %s' % self.code
        else:
            v = '%s / USD' % self.code
        if self.order != usd_order:
            return '%s Spot Exchange Rate' % v
        else:
            return 'Dollar'
            
    def info(self):
        return {'code': self.code,
                'isonumber': self.isonumber,
                'twolettercode': self.twolettercode,
                'order':self.order,
                'name':self.name,
                'raundoff':self.raundoff,
                'default_country': self.default_country}
        
    def printinfo(self):
        info = self.info()
        for k,v in info.items():
            print('%s: %s' % (k,v))
        
        
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.code)
    
    def __str__(self):
        return self.code
    
    def swap(self, c2):
        '''
        put the order of currencies as market standard
        '''
        inv = False
        c1 = self
        if c1.order > c2.order:
            ct = c1
            c1 = c2
            c2 = ct
            inv = True
        return inv,c1,c2
    
    def overusdfunc(self):
        if self.order > usd_order:
            return overusdfuni
        else:
            return overusdfun
    
    def usdoverfunc(self):
        if self.order > usd_order:
            return overusdfun
        else:
            return overusdfuni
    
    def spot(self, c2, v1, v2):
        if self.order > c2.order:
            vt = v1
            v1 = v2
            v2 = vt
        return v1/v2
    
    
class ccy_pair(object):
    '''
    Currency pair such as EURUSD, USDCHF
    
    XXXYYY - XXX is the foreign currency, while YYY is the base currency
    
    XXXYYY means 1 unit of of XXX cost XXXYYY units of YYY
    '''
    def __init__(self, c1, c2):
        self.ccy1 = c1
        self.ccy2 = c2
        self.code = '%s%s' % (c1,c2)
        self.id   = self.code
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.code)
    
    def __str__(self):
        return self.code
    
    def mkt(self):
        if self.ccy1.order > self.ccy2.order:
            return ccy_pair(self.ccy2,self.ccy1)
        else:
            return self
    


class ccydb(dict):
    
    def __init__(self, name):
        self.name = name
        
    def insert(self, c):
        self[c.code] = c


def currencydb():
    global _ccys
    if not _ccys:
        _ccys = make_ccys()
    return _ccys

def ccypairsdb():
    global _ccypairs
    if not _ccypairs:
        _ccypairs = make_ccypairs()
    return _ccypairs


def currency(code):
    c = currencydb()
    return c.get(str(code).upper(),None)

def ccypair(code):
    c = ccypairsdb()
    return c.get(str(code).upper(),None)

def currencypair(code):
    c = str(code)
    c1 = currency(c[:3])
    c2 = currency(c[3:])
    return ccy_pair(c1,c2)




def make_ccys():
    '''
    Create the currency dictionary
    '''
    db = ccydb('currencies')
    dfr = 4
    
    db.insert(ccy('EUR','978','EU',1, 'Euro', dfr,'EU'))
    db.insert(ccy('GBP','826','BP',2, 'British Pound', dfr,'GB'))
    db.insert(ccy('AUD','036','AD',3, 'Australian Dollar', dfr,'AU'))
    db.insert(ccy('NZD','554','ND',4, 'New-Zealand Dollar', dfr,'NZ'))
    db.insert(ccy('USD','840','UD',5, 'US Dollar', 0, 'US'))
    db.insert(ccy('CAD','124','CD',6, 'Canadian Dollar', dfr, 'CA'))
    db.insert(ccy('CHF','756','SF',7, 'Swiss Franc',dfr,'CH'))
    db.insert(ccy('NOK','578','NK',8, 'Norwegian Krona',dfr,'NO'))
    db.insert(ccy('SEK','752','SK',9, 'Swedish Krona',dfr,'SE'))
    db.insert(ccy('DKK','208','DK',10, 'Danish Krona',dfr,'DK'))
    db.insert(ccy('JPY','392','JY',10000,'Japanese Yen',2,'JP'))
    
    db.insert(ccy('CNY','156','CY',680,'Chinese Renminbi',dfr,'CN'))
    db.insert(ccy('KRW','410','KW',110000,'South Korean won',2,'KR'))
    db.insert(ccy('SGD','702','SD',15,'Singapore Dollar',dfr,'SG'))
    db.insert(ccy('IDR','360','IH',970000,'Indonesian Rupiah',0,'ID'))
    db.insert(ccy('THB','764','TB',3300,'Thai Baht',2,'TH'))
    db.insert(ccy('TWD','901','TD',18,'Taiwan Dollar',dfr,'TW'))
    db.insert(ccy('HKD','344','HD',19,'Hong Kong Dollar',dfr,'HK'))
    db.insert(ccy('PHP','608','PP',4770,'Philippines Peso',dfr,'PH'))
    db.insert(ccy('INR','356','IR',4500,'Indian Rupee',dfr,'IN'))
    db.insert(ccy('MYR','458','MR',345,'Malaysian Ringgit',dfr,'MY'))
    db.insert(ccy('VND','704','VD',1700000,'Vietnamese Dong',0,'VN'))
    
    db.insert(ccy('BRL','986','BC',200,'Brazilian Real',dfr,'BR'))
    db.insert(ccy('PEN','604','PS',220,'Peruvian New Sol',dfr,'PE'))
    db.insert(ccy('ARS','032','AP',301,'Argentine Peso',dfr,'AR'))
    db.insert(ccy('MXN','484','MP',1330,'Mexican Peso',dfr,'MX'))
    db.insert(ccy('CLP','152','CH',54500,'Chilean Peso',2,'CL'))
    db.insert(ccy('COP','170','CL',190000,'Colombian Peso',2,'CO'))
    db.insert(ccy('JMD','388','JD',410,'Jamaican Dollar',dfr,'JM'))              ### TODO: Check towletters code and position
    db.insert(ccy('TTD','780','TT',410,'Trinidad and Tobago Dollar',dfr,'TT'))   ### TODO: Check towletters code and position
    db.insert(ccy('BMD','060','BD',410,'BermudIan Dollar',dfr,'BM'))             ### TODO: Check towletters code and position
    
    db.insert(ccy('CZK','203','CK',28,'Czech Koruna',dfr,'CZ'))
    db.insert(ccy('PLN','985','PZ',29,'Polish Zloty',dfr,'PL'))
    db.insert(ccy('TRY','949','TY',30,'Turkish Lira',dfr,'TR'))
    db.insert(ccy('HUF','348','HF',32,'Hungarian Forint',dfr,'HU'))
    db.insert(ccy('RON','946','RN',34,'Romanian Leu',dfr,'RO'))
    db.insert(ccy('RUB','643','RR',36,'Russian Ruble',dfr,'RU'))
    db.insert(ccy('HRK','191','HK',410,'Croatian kuna',dfr,'HR'))                 ### TODO: Check towletters code and position
    db.insert(ccy('EEK','233','EK',410,'Estonia Kroon',dfr,'EE'))                 ### TODO: Check towletters code and position
    db.insert(ccy('KZT','398','KT',410,'Tenge',dfr,'KZ'))                         ### TODO: Check towletters code and position
    
    db.insert(ccy('ILS','376','IS',410,'Israeli Shekel',dfr,'IL'))
    db.insert(ccy('AED','784','AE',410,'United Arab Emirates Dirham',dfr,'AE'))   ### TODO: Check towletters code and position
    db.insert(ccy('QAR','634','QA',410,'Qatari Riyal',dfr,'QA'))                   ### TODO: Check towletters code and position
    db.insert(ccy('SAR','682','SR',410,'Saudi Riyal',dfr,'SA'))                    ### TODO: Check towletters code and position
    db.insert(ccy('EGP','818','EP',550,'Egyptian Pound',dfr,'EG'))
    db.insert(ccy('ZAR','710','SA',750,'South African Rand',dfr,'ZA'))
    return db


def make_ccypairs():
    ccys = currencydb()
    db   = ccydb('currencies pairs')
    
    for ccy1 in ccys.values():
        od = ccy1.order
        for ccy2 in ccys.values():
            if ccy2.order <= od:
                continue
            p = ccy_pair(ccy1,ccy2)
            db.insert(p)
    return db


_ccys = None
_ccypairs = None
