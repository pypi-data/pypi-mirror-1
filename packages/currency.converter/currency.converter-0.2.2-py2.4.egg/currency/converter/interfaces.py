from zope.interface import Attribute
from zope.interface import Interface
#from zope.schema import Choice
from zope.schema import Container
#from zope.schema import Float
#from zope.app.container.interfaces import IContained
#from zope.app.container.interfaces import IContainer
#from zope.app.container.interfaces import IContainerNamesContainer
#from zope.app.container.constraints import contains
from currency.converter import CurrencyConverterMessageFactory as _

class ICurrencyData(Interface):
    """CurrencyData itself"""

    def currency_data():
        """Returns the most recent currency data."""

    def updated_date():
        """Returns updated date."""

    def currency_codes():
        """Retrurns currency codes."""

    def currency_code_tuples():
        """Returns currency code and description tuples."""

    def currency_code_data():
        """Returns dictionary of currency code and rate list."""

    def currency_code_average(days):
        """Returns code and average"""

    def days():
        """Returns maximum gotten days."""

    def currency_rate_against_base_code(days, code):
        """Returns currency rate gainst base code."""

    def currency_rate_against_base_code_with_margin(days, code, margin):
        """Returns currency rate gainst base code with margin."""

class ICurrencyManager(Interface):
    """CurrencyManagerView"""

    def get_currency_data():
        """Method to get currency data for clock server."""
