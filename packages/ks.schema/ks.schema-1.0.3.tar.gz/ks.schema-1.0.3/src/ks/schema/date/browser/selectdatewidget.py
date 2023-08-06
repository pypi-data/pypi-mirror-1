### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SelectDateWidget class for the Zope 3 based ks.widget package

$Id: selectdatewidget.py 23861 2007-11-25 00:13:00Z xen $
"""

__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

import datetime

from zope.app.form.interfaces import ConversionError, InputErrors
from zope.app.form.browser.widget import SimpleInputWidget, renderElement

from ks.schema.date import _

class SelectDateWidget(SimpleInputWidget):

    tag = u'select'
    cssClass = u''
    extra = u''
    _missing = u''

    minYear = None
    maxYear = None

    minYearDelta = 100
    maxYearDelta = 0

    @property
    def _day_name(self):
        return self.name + '.day'

    @property
    def _month_name(self):
        return self.name + '.month'

    @property
    def _year_name(self):
        return self.name + '.year'

    def hasInput(self):
        return \
            self._day_name in self.request.form and \
            self._month_name in self.request.form and \
            self._year_name in self.request.form

    def _hasPartialInput(self):
        return \
            self._day_name in self.request.form or \
            self._month_name in self.request.form or \
            self._year_name in self.request.form

    def _getFieldInput(self, name):
        return self.request.form.get(name, self._missing)

    def _getFormInput(self):
        return (\
            self._getFieldInput(self._day_name),
            self._getFieldInput(self._month_name),
            self._getFieldInput(self._year_name))

    def _toFieldValue(self, (day, month, year)):
        if day == self._missing or month == self._missing or year == self._missing:
            return self.context.missing_value
        else:
            try:
                return datetime.date(int(year), int(month), int(day))
            except ValueError, e:
                raise ConversionError(_(u"Incorrect string data for date"), e)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            d = datetime.date.today()
            return (d.day, d.month, d.year)
        else:
            return (value.day, value.month, value.year)

    def _getFormValue(self):
        if not self._renderedValueSet():
            if self._hasPartialInput():
                error = self._error
                try:
                    try:
                        value = self.getInputValue()
                    except InputErrors:
                        return self._getFormInput()
                finally:
                    self._error = error
            else:
                value = self._getDefault()
        else:
            value = self._data
        return self._toFormValue(value)

    def _options(self, current, min, max, render=lambda x: x):
        if current != self._missing:
            try:
                current = int(current)
            except ValueError:
                current = self._missing
        if current == self._missing:
            current = min
        options = []
        for i in xrange(min, max + 1):
            if i == current:
                o = renderElement('option', value=i, contents=render(i), selected="selected")
            else:
                o = renderElement('option', value=i, contents=render(i))
            options.append(o)
        return ''.join(options)

    def _days(self, day):
        return self._options(day, 1, 31)

    def _months(self, month):
        names = self.request.locale.dates.calendars[u'gregorian'].getMonthNames()
        return self._options(month, 1, 12, lambda m: names[m - 1])

    def _years(self, year):
        minYear = self.minYear
        if minYear is None:
            minYear = datetime.date.today().year - int(self.minYearDelta)
        maxYear = self.maxYear
        if maxYear is None:
            maxYear = datetime.date.today().year + int(self.maxYearDelta)
        return self._options(year, minYear, maxYear)

    def __call__(self):
        value = self._getFormValue()
        ds = renderElement('select',
                           name=self._day_name,
                           id=self._day_name,
                           cssClass=self.cssClass,
                           extra=self.extra,
                           contents=self._days(value[0]))
        ms = renderElement('select',
                           name=self._month_name,
                           id=self._month_name,
                           cssClass=self.cssClass,
                           extra=self.extra,
                           contents=self._months(value[1]))
        ys = renderElement('select',
                           name=self._year_name,
                           id=self._year_name,
                           cssClass=self.cssClass,
                           extra=self.extra,
                           contents=self._years(value[2]))
        return ''.join((ds, ms, ys))

    def hidden(self):
        value = self._getFormValue()
        ds = renderElement('input',
                           name=self._day_name,
                           id=self._day_name,
                           type='hidden',
                           value=value[0],
                           extra=self.extra)
        ms = renderElement('input',
                           name=self._month_name,
                           id=self._month_name,
                           type='hidden',
                           value=value[1],
                           extra=self.extra)
        ys = renderElement('input',
                           name=self._year_name,
                           id=self._year_name,
                           type='hidden',
                           value=value[2],
                           extra=self.extra)
        return ''.join((ds, ms, ys))

class SelectDatetimeWidget(SelectDateWidget):

    @property
    def _hour_name(self):
        return self.name + '.hour'

    @property
    def _minute_name(self):
        return self.name + '.minute'

    @property
    def _second_name(self):
        return self.name + '.second'

    def hasInput(self):
        return super(SelectDatetimeWidget, self).hasInput() and \
                    self._hour_name in self.request.form and \
                    self._minute_name in self.request.form and \
                    self._second_name in self.request.form

    def _hasPartialInput(self):
        return super(SelectDatetimeWidget, self)._hasPartialInput() or \
            self._hour_name in self.request.form or \
            self._minute_name in self.request.form or \
            self._second_name in self.request.form

    def _getFormInput(self):
        return super(SelectDatetimeWidget, self)._getFormInput() +\
                    (self._getFieldInput(self._hour_name),
                    self._getFieldInput(self._minute_name),
                    self._getFieldInput(self._second_name))

    def _hours(self, hour):
        return self._options(hour, 0, 23)

    def _minutes(self, minute):
        return self._options(minute, 0, 59)

    def _seconds(self, second):
        return self._options(second, 0, 59)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            d = datetime.datetime.now()
            return (d.day, d.month, d.year, d.hour, d.minute, d.second)
        else:
            return (value.day, value.month, value.year, value.hour, value.minute, value.second)

    def _toFieldValue(self, (day, month, year, hour, minute, second)):
        if day == self._missing \
           or month == self._missing \
           or year == self._missing \
           or hour == self._missing \
           or minute == self._missing \
           or second == self._missing:
            return self.context.missing_value
        else:
            try:
                return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            except ValueError, e:
                raise ConversionError(_(u"Incorrect string data for date and time"), e)

    def __call__(self):
        res = super(SelectDatetimeWidget, self).__call__()
        value = self._getFormValue()
        return ''.join((res,
                        renderElement('select',
                           name=self._hour_name,
                           id=self._hour_name,
                           cssClass=self.cssClass,
                           extra=self.extra,
                           contents=self._hours(value[3])),
        renderElement('select',
                           name=self._minute_name,
                           id=self._minute_name,
                           cssClass=self.cssClass,
                           extra=self.extra,
                           contents=self._minutes(value[4])),
        renderElement('select',
                           name=self._second_name,
                           id=self._second_name,
                           cssClass=self.cssClass,
                           extra=self.extra,
                           contents=self._seconds(value[5]))))

    def hidden(self):
        res = super(SelectDatetimeWidget, self).hidden()
        value = self._getFormValue()
        return ''.join((res,
                        renderElement('input',
                           name=self._hour_name,
                           id=self._hour_name,
                           type='hidden',
                           value=value[3],
                           extra=self.extra),
        renderElement('input',
                           name=self._minute_name,
                           id=self._minute_name,
                           type='hidden',
                           value=value[4],
                           extra=self.extra),
        renderElement('input',
                           name=self._second_name,
                           id=self._second_name,
                           type='hidden',
                           value=value[5],
                           extra=self.extra)))
