### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based htmlwidget package

$Id: interfaces.py 35330 2008-01-13 09:03:40Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

from zope.interface import Interface, Attribute

from ks.schema.html import _

class IHTMLImageListProvider(Interface):
    """Something having an image list for an html editor"""

    images = Attribute(_(u"""List of 2-tuples:
        [('alt 1', 'src 1'), ('alt 2', 'src 2'), ...]
        """))
