### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the search object widget Zope 3 based package

$Id: interfaces.py 35330 2008-01-13 09:03:40Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

from zope.interface import Interface
from zope.app.form.browser.interfaces import IBrowserWidget, \
                                             IInputWidget, \
                                             ITextBrowserWidget

from ks.schema.date import _

class ICalendarWidget(ITextBrowserWidget):
    """Interface for Calendar Widget"""