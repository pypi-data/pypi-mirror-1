##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Trivial adapter that adapts a zope.i18n locale to a collator

This adapter takes an object that has a getLocaleID method that
returns a locale string.  It returns a Collator for the given locale:

    >>> class Locale:
    ...     def __init__(self, id):
    ...         self.id = id
    ...     def getLocaleID(self):
    ...         return self.id

    >>> collator = LocaleCollator(Locale('da_DK'))
    >>> collator.__class__.__name__
    'Collator'

    >>> collator.locale
    'da_DK'

Note that we're not declaring any interfaces so as to avoid creating
a dependency on zope.i18n.locales.

$Id: localeadapter.py 67613 2006-04-26 08:21:40Z dobe $
"""
from zope.ucol import Collator

def LocaleCollator(locale):
    return Collator(str(locale.getLocaleID()))
    
