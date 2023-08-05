### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""HMTMLDisplayWidget class for the Zope 3 based ks.widget package

$Id: smarturi.py 35330 2008-01-13 09:03:40Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

from zope.schema import Object
from interfaces import ISmartURI, IURI
from zope.interface import implements
from zope.interface.interfaces import IInterface

class URI(object):

    implements(IURI)

    title = IURI['title'].default

    uri = IURI['uri'].default

    def __init__(self, title=None, uri=None):
        self.title = title
        self.uri = uri

class SmartURI(Object):

    implements(ISmartURI)

    def __init__(self, **kw):
        schema = kw.get('schema', None)
        if not IInterface.providedBy(schema):
            schema = IURI
        super(SmartURI, self).__init__(schema, **kw)
