### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based ks.schema.captcha package

$Id: interfaces.py 35330 2008-01-13 09:03:40Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

from zope.schema.interfaces import IField
from zope.schema import TextLine, ASCIILine, ValidationError
from zope.interface import Interface, Attribute
from zope.schema.interfaces import ValidationError
from ks.schema.captcha import _

class CodeIsInvalidError(ValidationError):
    __doc__ = _(u'Codes is not equal!')

class ICaptcha(IField):
    """Captcha interface"""

    captcha = Attribute("captcha",
                             ("ks.captcha.interfaces.ICaptcha to be used, or image checker utility name, or None.\n"
                             "\n"
                             "If a string, the image checker name should be used by an\n"
                             "registered ks.captcha.interfaces.ICaptcha utility name"))
