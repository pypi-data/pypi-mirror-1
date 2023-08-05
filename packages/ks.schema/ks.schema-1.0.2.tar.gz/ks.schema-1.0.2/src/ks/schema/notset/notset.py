### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""NotSetMixin class for the Zope 3 based ks.schema.notset package

$Id: notset.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from zope.schema import Bytes, Bool

class NotSetMixin(object):

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))

class BytesNotSet(NotSetMixin, Bytes):
    """Bytes Not Set"""

class BoolNotSet(NotSetMixin, Bool):
    """Bool Not Set"""
