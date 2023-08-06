### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Captcha class for the Zope 3 based ks.schema.captcha package

$Id: captcha.py 35233 2007-11-28 11:56:17Z anton $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35233 $"
__date__ = "$Date: 2007-11-28 13:56:17 +0200 (Wed, 28 Nov 2007) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from zope.schema import Field
from zope.schema.interfaces import RequiredMissing
from interfaces import ICaptcha, CodeIsInvalidError
from zope.interface import implements
from zope.interface.interfaces import IInterface
import ks.captcha.interfaces
from zope.component import getSiteManager, getUtility
import random
from zope.security import checkPermission
from ks.schema.notset.notset import NotSetMixin
from ks.schema.captcha import _

class Captcha(NotSetMixin, Field):

    implements(ICaptcha)

    def __init__(self, captcha=None, **kw):
        """Initialize object."""
        if captcha is not None:
            assert (isinstance(captcha, basestring)
                    or ks.captcha.interfaces.ICaptcha.providedBy(captcha))

        self.captcha = None
        self.captchaName = ''
        if isinstance(captcha, (unicode, str)):
            self.captchaName = captcha
        else:
            self.captcha = captcha
        self._init_field = bool(self.captchaName)
        super(Captcha, self).__init__(**kw)
        self._init_field = False

    def bind(self, object):
        """See zope.schema._bootstrapinterfaces.IField."""
        clone = super(Captcha, self).bind(object)
        # get registered vocabulary if needed:
        if ks.captcha.interfaces.ICaptcha.providedBy(self.captcha):
            clone.captcha = self.captcha
            assert ks.captcha.interfaces.ICaptcha.providedBy(clone.captcha)
        elif clone.captcha is None:
            clone.captcha = getUtility(ks.captcha.interfaces.ICaptcha, name=self.captchaName, context=object)
            assert ks.captcha.interfaces.ICaptcha.providedBy(clone.captcha)

        return clone

    def _validate(self, value):
        # Pass all validations during initialization
        if self._init_field:
            return
        super(Captcha, self)._validate(value)
        captcha = self.captcha
        if captcha is None:
            try:
                captcha = getUtility(ks.captcha.interfaces.ICaptcha, name=self.captchaName, context=self.context)
            except TypeError:
                raise ValueError("Can't validate value without image checker")
        if not checkPermission("ks.schema.captcha.canPassCaptcha", self.context):
            if value[1] is None:
                raise RequiredMissing
            if not captcha.check(*value):
                raise CodeIsInvalidError(value)
