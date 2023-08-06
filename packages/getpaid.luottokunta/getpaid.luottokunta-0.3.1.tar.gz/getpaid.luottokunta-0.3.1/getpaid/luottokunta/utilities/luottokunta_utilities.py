from zope.interface import implements
from decimal import Decimal, ROUND_HALF_UP
from getpaid.luottokunta.interfaces import ILuottokuntaLanguage, IDecimalPrice

class LuottokuntaLanguage(object):

    implements(ILuottokuntaLanguage)

    def __call__(self, language_bindings):
        """Returns language variable."""
        languages = (("fi", "FI"), ("sv", "SE"), ("en", "EN"))
        language_priority = [language_bindings[0]] + [language_bindings[1]] + language_bindings[2]
        for language in language_priority:
            for lang in languages:
                if language == lang[0]:
                    return lang[1]
        else:
            return languages[2][1]

class DecimalPrice(object):
    implements(IDecimalPrice)
    def __call__(self, price):
        if price is None:
            return None
        if type(price).__name__ == 'float':
            price = str(price)
        price = Decimal(price).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)
        price = Decimal(price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        return price
