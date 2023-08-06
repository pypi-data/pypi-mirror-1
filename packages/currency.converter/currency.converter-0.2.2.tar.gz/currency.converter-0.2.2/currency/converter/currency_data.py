from persistent import Persistent
from zope.interface import implements
from currency.converter.interfaces import ICurrencyData
from elementtree.ElementTree import XML, ElementTree, Element
import urllib2
from currencies import currencies

class CurrencyData(Persistent):
    implements(ICurrencyData)

    def __init__(self):
        self.currencies = None
        self.selected_base_currency = "EUR"
        self.selected_days = 1
        self.margin = 0.00

    def currency_data(self):
        """Returns the most recent currency data with tuples."""
        etree90 = ElementTree()
#        data90 = urllib2.urlopen('http://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml')
#        root90 = ElementTree.parse(etree90, data90)
#        DATA90 = root90[2]
#        DATA_list = []
#        for DATA in DATA90:
#            daily_data_list = []
#            for daily_data in DATA:
#                daily_data_tuple = (daily_data.get('currency'), daily_data.get('rate'))
#                daily_data_list.append(daily_data_tuple)
#            ddl = (DATA.get('time'), dict(daily_data_list))
#            DATA_list.append(ddl)
#        return DATA_list

        try:
            data90 = urllib2.urlopen('http://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml')
            root90 = ElementTree.parse(etree90, data90)
            DATA90 = root90[2]
            DATA_list = []
            for DATA in DATA90:
                daily_data_list = []
                for daily_data in DATA:
                    daily_data_tuple = (daily_data.get('currency'), daily_data.get('rate'))
                    daily_data_list.append(daily_data_tuple)
                ddl = (DATA.get('time'), dict(daily_data_list))
                DATA_list.append(ddl)
            return DATA_list
        except:
            return False

    def updated_date(self):
        """Returns updated date."""
#        return self.currency_data()[0][0]
        if self.currencies != None:
            return self.currencies[0][0]
        else:
            return False

    def currency_codes(self):
        """Retrurns currency codes."""
        codes = ['EUR']
        if self.currencies != None:
            for date in self.currencies:
                for key in date[1].keys():
                    if key not in codes:
                        codes.append(key)
        return codes

    def currency_code_tuples(self):
        """Returns currency code and description tuples."""
#        if self.currency_codes() != False:
        results = []
        for code in self.currency_codes():
            t = (code, currencies[code])
            results.append(t)
        return results

    def currency_code_data(self):
        """Returns dictionary of currency code and rate list."""
        if self.currencies != None:
            currency_data_withought_date = []
#        for data in self.currency_data():
            for data in self.currencies:
                currency_data_withought_date.append(data[1])
#            r = []
            r = {}
            for code in self.currency_codes():
                results = []
                for data in currency_data_withought_date:
                    for key in data.keys():
                        if code == key:
                            results.append(data[key])
#                r.append({code:results})
                r.update({code:results})
            return r
        else:
            return False

    def currency_code_average(self, days):
        """Returns code and average"""
        if self.currencies != None:
            results = {}
            for (code, L) in self.currency_code_data().items():
#            length = len(L)
#            results.update({code:length})
                if code == 'EUR':
                    rate = 1
                    results.update({code:rate})
                elif len(L) >= days > 0:
                    L = L[0:days]
                    S = 0
                    for l in L:
                        S = S + float(l)
                    rate = S / days
                    results.update({code:rate})
                elif days > len(L) > 0:
                    S = 0
                    for l in L:
                        S = S + float(l)
                    rate = S / len(L)
                    results.update({code:rate})
                else:
                    pass
            return results
        else:
            return False

    def days(self):
        """Returns maximum gotten days."""
        if self.currencies != None:
            return range(1,len(self.currencies)+1)
        else:
            return [1]

    def currency_rate_against_base_code(self, days, code):
        """Returns currency rate gainst base code."""
        if self.currencies != None:
            if code == "EUR":
                cca = self.currency_code_average(days)
                del cca[code]
                return cca
            else:
                cca = self.currency_code_average(days)
                code_value = float(cca[code])
                del cca[code]
                results = {}
                for (k, v) in cca.items():
                    v = float(v) / code_value
                    results.update({k:v})
                return results
        else:
            return False

    def currency_rate_against_base_code_with_margin(self, days, code, margin):
        """Returns currency rate gainst base code with margin."""
        if self.currencies != None:
            results = {}
            for (k, v) in self.currency_rate_against_base_code(days, code).items():
                v = v * (100 + margin) / 100
                results.update({k:v})
            return results
        else:
            return False
