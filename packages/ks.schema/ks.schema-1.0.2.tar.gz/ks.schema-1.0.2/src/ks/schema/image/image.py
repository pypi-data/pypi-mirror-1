### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Image field class for the Zope 3 based ks.schema.image package

$Id: image.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

from zope.schema import Bytes
from zope.interface import implements

from interfaces import IImage


class Image(Bytes):
    implements(IImage)
