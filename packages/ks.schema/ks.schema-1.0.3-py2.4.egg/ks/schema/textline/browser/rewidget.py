### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""The widget regular expression classes.

$Id: rewidget.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Arvid"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.schema.interfaces import ValidationError
from zope.app.form.browser.textwidgets import TextWidget, PasswordWidget
from zope.app.form.interfaces import WidgetInputError
from zope.app.form.browser.widget import SimpleInputWidget
from zope.schema.interfaces import InvalidValue
from ks.schema.textline import _

import re

dot_atom = r'[-A-Za-z0-9!#$%&\'*+/=?^_{|}~]+'
domain = r'[-A-Za-z0-9]'

emailConstraint = re.compile(r'^%(dot_atom)s(?:\.%(dot_atom)s)*@%(domain)s+(?:\.%(domain)s+)*(?:\.%(domain)s{2,})+$' % {'dot_atom': dot_atom, 'domain' : domain})
nameConstraint = re.compile(u'^[a-zA-Z0-9_-]{2,}$', flags=re.U)

class NotValidName(ValidationError):
    __doc__ = _(u"""Alias must be min 2 characters length and consist of a-z A-Z, -, _ and 0-9""")

class NotValidEmail(ValidationError):
    __doc__ = _(u"""Email must be in format:
        local part (symbols, separated by .),
        sign @, domain (characters, 0-9, -,
        separated by ., and length of first-level domain 2 characters min).
        symbols - это latin characters, numbers,
        !, #, $, %, &, ', *, +, -, /, =, ?, ^, _, {, |, }, ~
    """)

class WidgetREBase(TextWidget):
    """widget re checker"""
    reObj = None
    exceptionRE = ValidationError

    def getInputValue(self):
        value = super(WidgetREBase, self).getInputValue()

        if value and not (hasattr(self, '_error') and self._error):
            try:
                if self.reObj.match(value) is None:
                    raise self.exceptionRE
            except self.exceptionRE, v:
                self._error = WidgetInputError(self.context.__name__, self.label, v)
                raise self._error

        return value

class EmailWidget(WidgetREBase):
    """e-mail widget"""
    reObj = emailConstraint
    exceptionRE = NotValidEmail

class NameWidget(WidgetREBase):
    """name widget"""
    reObj = nameConstraint
    exceptionRE = NotValidName
