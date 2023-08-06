### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based ks.schema.captcha package

$Id: interfaces.py 35231 2007-11-28 11:26:59Z anton $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35231 $"
__date__ = "$Date: 2007-11-28 13:26:59 +0200 (Wed, 28 Nov 2007) $"

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
