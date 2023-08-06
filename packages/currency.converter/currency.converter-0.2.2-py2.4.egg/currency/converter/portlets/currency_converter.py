from zope.component import (getMultiAdapter,
                            queryUtility,
                            getUtility)

from zope.interface import implements
from zope import schema
from zope.formlib import form

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from currency.converter import CurrencyConverterMessageFactory as _
from currency.converter.browser.currency_manager import CurrencyManagerView
from currency.converter.browser.currency_converter_viewlet import CurrencyConverterViewlet

from currency.converter.interfaces import ICurrencyData
from currency.converter.currencies import currencies


from zope.interface import implements, directlyProvides
#from zope.component import adapts

#from zope.schema.interfaces import IVocabularyFactory
#from zope.schema.vocabulary import SimpleVocabulary

class ICurrencyConverterPortlet(IPortletDataProvider):
    """ICurrencyConverterPortlet"""
#    default_base_currency = schema.Choice(
#        title=_(u"Default base currency"),
#        description=_(u""),
#        required=False,
#        vocabulary=u"currency.converter.CurrencyCodeName",
#        )

class Assignment(base.Assignment):
    implements(ICurrencyConverterPortlet)

    @property
    def title(self):
        return _(u'Currency Converter')

class Renderer(base.Renderer, CurrencyConverterViewlet):

    render = ViewPageTemplateFile('currency_converter.pt')

    def update(self):
         CurrencyConverterViewlet.update(self)
##        ## Defines.
#        form = self.request.form
#        currency_data = getUtility(ICurrencyData)

#        self.currency_data = currency_data.currencies
#        self.updated_date = currency_data.updated_date()
#        self.currency_code_tuples = currency_data.currency_code_tuples()
#        self.days = currency_data.days()
#        self.selected_base_currency = currency_data.selected_base_currency
#        self.selected_days = currency_data.selected_days
#        self.margin = currency_data.margin
##        self.currencies = currency_data.currency_rate_against_base_code_with_margin(int(self.selected_days), self.selected_currency, self.margin)

#        try:
#            self.base_currency_rate = form.get('base_currency_rate', 1)
#        except:
#            self.base_currency_rate = 1
##        try:
##            self.base_currency = form.get('base_currency', 'EUR')
##        except:
##            self.base_currency = 'EUR'
#        try:
#            self.selected_base_currency_code = form.get('base_currency_code', self.selected_base_currency)
#        except:
#            self.selected_base_currency_code = self.selected_base_currency
#        try:
#            self.selected_currency_code = form.get('currency_code', None)
#        except:
#            self.selected_currency_code = None


#        self.calculated_rate = None

#        self.error_message = None

#        ## Check buttons.
#        convert_button = form.get('form.button.Convert', None) is not None

#        if convert_button:
#            if form.get('base_currency_code') != form.get('currency_code'):
#                self.base_currency_rate = form.get('base_currency_rate')
#                self.base_currency_code = form.get('base_currency_code')
#                self.currency_code = form.get('currency_code')
#                self.calculated_rate = self.calculated_rate_against_base_rate(float(self.base_currency_rate), self.base_currency_code, self.currency_code)
#                return self.render()
#            else:
#                self.error_message =_(u"Please choose different currencies.")
#                return self.render()

#        else:
#            return self.render()

#    def calculated_rate_against_base_rate(self, base_currency_rate, base_currency_code, currency_code):
#        """Returns calculated rate against base currency rate."""
#        currency_data = getUtility(ICurrencyData)
#        days = currency_data.selected_days
#        margin = currency_data.margin
#        currency_dictionary = currency_data.currency_rate_against_base_code_with_margin(days, base_currency_code, margin)
#        result = currency_dictionary[currency_code] * base_currency_rate
#        return '%.2f' %result

    def current_url(self):
        """Returns current url"""
        context= aq_inner(self.context)
        context_state = self.context.restrictedTraverse("@@plone_context_state")
        url = context_state.current_page_url()
        return '%s' % (url,)

    @property
    def available(self):
        currency_data = getUtility(ICurrencyData)
        if currency_data.currencies:
            return True
        else:
            return False

    def link_to_currency_list(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        return '%s/@@currency-converter' % portal_url


class AddForm(base.AddForm):
    form_fields = form.Fields(ICurrencyConverterPortlet)
    label = _(u"Add Currency Converter portlet")
    description =_(u"This portlet displays currencies where you can check various of currency rates.")

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    form_fields = form.Fields(ICurrencyConverterPortlet)
    label = _(u"Edit Currency Converter portlet")
    description =_(u"This portlet displays currencies where you can check various of currency rates.")
