The code is distributed under terms of the Zope Public License version 2.1.
See also LICENSE.txt.

z3locales
=========

Z3locales is a library which translates dates in Zope 2 to the current
user language using Zope 3 technology.

Those functions are available in ``localdatetime``:

``getFormattedNow``
    Return the current date formatted and translated in the current user language.

``getFormattedDate`` 
    Take a date (should be a tuple ``(year, month, day[, hour[,
    minute[, second]]])``), format it and translate it in the current
    user language.

``getMonthNames``
    Return a list of month names translated in the current user language.

``getMonthAbbreviations``
    Return a list of month abbreviations (usually the first three
    letters) translated in the current user language.


