from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from currency.converter import CurrencyConverterMessageFactory as _

#from zope.component import getMultiAdapter
from zope.component import getUtility

#from currency.converter.interfaces import ICurrencyManager
from currency.converter.interfaces import ICurrencyData

class CurrencyConverterView(BrowserView):
    """View for currency manager."""

    template = ViewPageTemplateFile('templates/currency_converter.pt')

    def __call__(self):

#        ## Hide the editable-object border.
        self.request.set('disable_border', True)

#        ## Defines.
        form = self.request.form

        ## Data from ICurrencyData
        currency_data = getUtility(ICurrencyData)
        self.currency_data = currency_data.currencies
        self.updated_date = currency_data.updated_date()
        self.currency_code_tuples = currency_data.currency_code_tuples()
        self.days = currency_data.days()
        self.selected_base_currency = currency_data.selected_base_currency
        self.selected_days = currency_data.selected_days
        self.margin = currency_data.margin
#        self.currencies = currency_data.currency_rate_against_base_code_with_margin(int(self.selected_days), self.selected_currency, self.margin)

        try:
            self.base_currency_rate = form.get('base_currency_rate', 1)
        except:
            self.base_currency_rate = 1
#        try:
#            self.base_currency = form.get('base_currency', 'EUR')
#        except:
#            self.base_currency = 'EUR'
        try:
            self.selected_base_currency_code = form.get('base_currency_code', self.selected_base_currency)
        except:
            self.selected_base_currency_code = self.selected_base_currency
        try:
            self.selected_currency_code = form.get('currency_code', None)
        except:
            self.selected_currency_code = None


        self.calculated_rate = None

        self.error_message = None

        ## Check buttons.
        convert_button = form.get('form.button.Convert', None) is not None

        if convert_button:
            if form.get('base_currency_code') != form.get('currency_code'):
                self.base_currency_rate = form.get('base_currency_rate')
                self.base_currency_code = form.get('base_currency_code')
                self.currency_code = form.get('currency_code')
                self.calculated_rate = self.calculated_rate_against_base_rate(float(self.base_currency_rate), self.base_currency_code, self.currency_code)
                return self.template()
            else:
                self.error_message =_(u"Please choose different currencies.")
                return self.template()

        else:
            return self.template()

    def calculated_rate_against_base_rate(self, base_currency_rate, base_currency_code, currency_code):
        """Returns calculated rate against base currency rate."""
        currency_data = getUtility(ICurrencyData)
        days = currency_data.selected_days
        margin = currency_data.margin
        currency_dictionary = currency_data.currency_rate_against_base_code_with_margin(days, base_currency_code, margin)
        result = currency_dictionary[currency_code] * base_currency_rate
        return '%.2f' %result
#        return currency_dictionary[currency_code]
#        return currency_dictionary["USD"]
