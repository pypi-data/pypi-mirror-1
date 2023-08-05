### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""CaptchaDemo class for the Zope 3 based ks.schema.captcha.demo package

$Id: captchademo.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from interfaces import ICaptchaDemo
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained

class CaptchaDemo(Persistent, Contained):

    implements(ICaptchaDemo)
