### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Simple Widget Factories module for the Zope 3 based ks.widget package

$Id: simplewidgetfactory.py 23861 2007-11-25 00:13:00Z xen $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

import zope.component
from zope.app.form import CustomWidgetFactory
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
import logging
logger = logging.getLogger('ks.widget.simplewidgetfactory')

def SchemaDisplayWidgetFactory(field, *args, **kw):
        # `field` is a bound field
        return CustomWidgetFactory(lambda *kv, **kw: zope.component.getMultiAdapter(
            (field, args[-1]), IDisplayWidget), *args, **kw)(field, args[-1])

def AddFormWidgetFactory(field, *args, **kw):
        # `field` is a bound field
        return CustomWidgetFactory(lambda *kv, **kw: zope.component.getMultiAdapter(
            (field, args[-1]), IInputWidget), *args, **kw)(field, args[-1])

def EditFormWidgetFactory(field, *args, **kw):
        # `field` is a bound field
        if field.readonly:
            iface = IDisplayWidget
        else:
            iface = IInputWidget
        return CustomWidgetFactory(lambda *kv, **kw: zope.component.getMultiAdapter(
            (field, args[-1]), iface), *args, **kw)(field, args[-1])
