from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from currency.converter import CurrencyConverterMessageFactory as _

from zope.component import getMultiAdapter
from zope.component import queryUtility

from currency.converter.interfaces import ICurrencyData

class CurrencyManagerView(BrowserView):
    """View for currency manager."""

    template = ViewPageTemplateFile('templates/currency_manager.pt')

    def __call__(self):

#        ## Hide the editable-object border.
        self.request.set('disable_border', True)

#        ## Defines.
        form = self.request.form
        currency_data = queryUtility(ICurrencyData)
        if currency_data.currency_data():
            currency_data.currencies = currency_data.currency_data()
        self.updated_date = currency_data.updated_date()
        self.currency_code_tuples = currency_data.currency_code_tuples()
        self.days = currency_data.days()
        self.selected_currency = currency_data.selected_base_currency
        self.selected_days = currency_data.selected_days
        self.margin = currency_data.margin
        self.currencies = currency_data.currency_rate_against_base_code_with_margin(int(self.selected_days), self.selected_currency, self.margin)
        if self.currencies != False:
            self.currency_rate = self.currencies.items()
        else:
            self.currency_rate = False
        self.error_message = False

        ## Check buttons.
        update_button = form.get('form.button.Update', None) is not None

        if update_button:
            try:
                float(form.get('margin'))
                self.margin = float(form.get('margin'))
                currency_data.margin = self.margin
            except:
                self.error_message = _(u"Please input float like 5.00")
            self.selected_currency = form.get('currency_code')
            currency_data.selected_base_currency = self.selected_currency
            self.selected_days = int(form.get('days'))
            currency_data.selected_days = self.selected_days
            self.currencies = currency_data.currency_rate_against_base_code_with_margin(self.selected_days, self.selected_currency, self.margin)
            self.currency_rate = self.currencies.items()
            return self.template()

        else:
            return self.template()
