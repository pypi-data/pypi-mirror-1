### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based smartimagecache package

$Id: interfaces.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

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
