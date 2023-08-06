from zope.interface import implements
from getpaid.verkkomaksut.interfaces import ILanguageCulture

class LanguageCulture(object):

    implements(ILanguageCulture)

    def __call__(self, language_bindings):
        """Returns verkkomaksut culture."""
        cultures = (("fi", "fi_FI"), ("sv", "sv_SE"), ("ru", "ru_RU"), ("en", "en_US"))
        language_priority = [language_bindings[0]] + [language_bindings[1]] + language_bindings[2]
        for language in language_priority:
            for culture in cultures:
                if language == culture[0]:
                    return culture[1]
        else:
            return cultures[3][1]
