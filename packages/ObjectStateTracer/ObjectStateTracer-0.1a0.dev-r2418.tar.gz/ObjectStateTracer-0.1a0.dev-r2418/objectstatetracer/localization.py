import pkg_resources

from gettext import translation

from turbogears.i18n.utils import get_locale
from turbogears.i18n.tg_gettext import gettext as tg_gettext, lazify
from turbogears.util import request_available

_locales_dir = pkg_resources.resource_filename('objectstatetracer', 'locales')
_catalogs = dict()

def _get_ost_translation(locale):
    return translation(domain='messages', localedir=_locales_dir, 
                       languages=[locale])

class NotSpecified: pass

def plain_gettext(key, locale=NotSpecified, domain=NotSpecified):
    if locale is NotSpecified:
        locale = get_locale()
    
    if _catalogs.has_key(locale):
        return _catalogs[locale](key)
    
    try:
        ugettext = _catalogs[locale] = _get_ost_translation(locale).ugettext
    except IOError:
        ugettext = _catalogs[locale] = tg_gettext
    
    return ugettext(key)

lazy_gettext = lazify(plain_gettext)

def gettext_ost(key, locale=NotSpecified, domain=NotSpecified):
    """Gets the gettext value for key. Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used. If locale is None, gets the value provided by get_locale.
     """
    
    if request_available():
        return plain_gettext(key, locale, domain)
    else:
        return lazy_gettext(key, locale, domain)