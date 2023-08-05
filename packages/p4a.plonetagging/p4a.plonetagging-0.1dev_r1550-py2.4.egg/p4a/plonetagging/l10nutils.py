import datetime
import DateTime
import pytz
import pytz.zoneinfo.GMT
import time
import zope.component
import zope.i18n.interfaces
import zope.i18n.locales
import zope.interface
import zope.interface.common.idatetime

class ServerTZInfo(pytz.UTC.__class__):
    """Default tzinfo adapter that will add the current server tzinfo
    during a normalize call.

      >>> from datetime import datetime
      >>> tzinfo = ServerTZInfo()
      >>> normalized = tzinfo.normalize(datetime.now())
    """

    zope.interface.implements(zope.interface.common.idatetime.ITZInfo)
    zope.component.adapts(zope.interface.Interface)

    def __init__(self, context=None):
        # context not needed
        pass

    def normalize(self, dt):
        tzinfo = dt.tzinfo
        if tzinfo == None:
            tzstr = DateTime.DateTime(str(dt)).timezone()
            if tzstr.startswith('GMT'):
                offset = int(tzstr[3:])
                tzinfo = pytz.zoneinfo.GMT.GMT.__class__()
                tzinfo.zone = 'GMT' + str(offset)
                tzinfo._utcoffset = datetime.timedelta(hours=offset)
                tzinfo._tzname = tzinfo.zone
            else:
                tzinfo = pytz.timezone(tzstr)

        return dt.replace(tzinfo=tzinfo)

def derive_locale(request):
    envadapter = zope.i18n.interfaces.IUserPreferredLanguages(request)
    langs = envadapter.getPreferredLanguages()
    for httplang in langs:
        parts = (httplang.split('-') + [None, None])[:3]
        try:
            return zope.i18n.locales.locales.getLocale(*parts)
        except zope.i18n.locales.LoadLocaleError:
            # Just try the next combination
            pass
    else:
        # No combination gave us an existing locale, so use the default,
        # which is guaranteed to exist
        return zope.i18n.locales.locales.getLocale(None, None, None)

    return None
