from zope.interface import implements
from getpaid.luottokunta.interfaces import ILuottokuntaLanguage

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
