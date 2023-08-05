### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based smartimagecache package

$Id: interfaces.py 35330 2008-01-13 09:03:40Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

from zope.schema.interfaces import IObject
from zope.schema import TextLine, ASCIILine
from zope.interface import Interface
from ks.schema.smarturi import _

class IURI(Interface):
    """URI interface"""

    title = TextLine(title=_(u'URI title'),
                     required=False)

    uri = ASCIILine(title=_(u'URI'),)


class ISmartURI(IObject):
    """Smart URI Field"""
