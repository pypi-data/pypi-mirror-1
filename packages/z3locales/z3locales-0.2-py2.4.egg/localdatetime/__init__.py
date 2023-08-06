# Copyright (c) 2004-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.i18n.locales import locales

def normalize_lang(lang):
    lang = lang.strip().lower()
    lang = lang.replace('_', '-')
    lang = lang.replace(' ', '')
    return lang

def getlocaleinfo(self):
    request = self.REQUEST
    accept_langs = request.get('HTTP_ACCEPT_LANGUAGE', '').split(',')

    # Normalize lang strings
    accept_langs = map(normalize_lang, accept_langs)
    # Then filter out empty ones
    accept_langs = filter(None, accept_langs)

    length = len(accept_langs)
    accepts = []

    for index, lang in enumerate(accept_langs):
        l = lang.split(';', 2)

        quality = None

        if len(l) == 2:
            q = l[1]
            if q.startswith('q='):
                q = q.split('=', 2)[1]
                quality = float(q)
        else:
            # If not supplied, quality defaults to 1
            quality = 1.0

        if quality == 1.0:
            # ... but we use 1.9 - 0.001 * position to
            # keep the ordering between all items with
            # 1.0 quality, which may include items with no quality
            # defined, and items with quality defined as 1.
            quality = 1.9 - (0.001 * index)

        accepts.append((quality, l[0]))

    # Filter langs with q=0, which means
    # unwanted lang according to the spec
    # See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
    accepts = filter(lambda acc: acc[0], accepts)

    accepts.sort()
    accepts.reverse()

    return [lang for quality, lang in accepts]


def getFormattedNow(self):
    from datetime import datetime
    import time
    now = time.gmtime()
    d = datetime(*now[:6])
    l = getlocaleinfo(self)[0]
    parts = l.split('-')
    formatter = locales.getLocale(*parts).dates.getFormatter('dateTime', 'full')
    return formatter.format(d)

__marker__ = []
def getFormattedDate(self, date, size="full", locale=__marker__, display_time=True):
    """return a formatted date

        date should be a tuple (year, month, day[, hour[, minute[, second]]])
    """
    from datetime import datetime
    d = datetime(*date)
    l = locale
    if l is __marker__:
        l = getlocaleinfo(self)[0]
    parts = l.split('-')
    format = 'dateTime'
    if not display_time:
      format = 'date'
    formatter = locales.getLocale(*parts).dates.getFormatter(format, size)
    return formatter.format(d)

def getMonthNames(self, locale=None, calendar='gregorian'):
    """returns a list of month names for the current locale"""
    l = locale
    if l is None:
        l = getlocaleinfo(self)[0]
    parts = l.split('-')
    return locales.getLocale(*parts).dates.calendars[calendar].getMonthNames()

def getMonthAbbreviations(self, locale=None, calendar='gregorian'):
    """returns a list of abbreviated month names for the current locale"""
    l = locale
    if l is None:
        l = getlocaleinfo(self)[0]
    parts = l.split('-')
    return locales.getLocale(*parts).dates.calendars[calendar].getMonthAbbreviations()
