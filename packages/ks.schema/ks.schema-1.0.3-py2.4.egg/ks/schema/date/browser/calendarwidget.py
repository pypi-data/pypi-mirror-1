### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the search object widget Zope 3 based package

$Id: calendarwidget.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.interface import implements
from zope.app.form.browser import DateWidget
from zope.app.form.browser.widget import renderElement, renderTag
from zc.resourcelibrary import need
from zope.app.zapi import absoluteURL
from interfaces import ICalendarWidget

from ks.schema.date import _

SELECT_DATE_BUTTON_NAME = _(u'...')

RESOURCE_LIBRARY = 'ks.schema.date.browser.calendarwidget'

CALENDAR_SETUP = """Calendar.setup({
    inputField     :    "%(input_id)s",     // id of the input field
    displayArea      :    "%(displayArea)s",
    //button         :    "%(button_id)s",  // trigger for the calendar (button ID)
    align          :    "Bl",           // alignment (defaults to "Bl")
    singleClick    :    true,
    dateStatusFunc :    ourDateStatusFunc,
    date          :    "%(date)s",
    ifFormat      :    "%(format)s",
    daFormat      :    "%(displayformat)s",
    onSelect      :    onSelect,
});"""

CALENDAR_HTML = """<div id="calendar-top">
    <a href="#" class="next"><img src="%(resource_url)s/btn/next.gif" border="0" alt="" width="22" height="19" /></a>
    <a href="#" class="prev"><img src="%(resource_url)s/btn/prev.gif" border="0" alt="" width="22" height="19" /></a>
    <p class="date" id="%(displayArea)s">%(value)s</p>
    <div class="clear"></div>
</div>"""

import zope.component

class CalendarWidget(DateWidget):
    """Base Class For Search Object Fields"""

    implements(ICalendarWidget)

    @property
    def selectDateButtonName(self):
        return '%s-button' % self.name

    @property
    def buttonId(self):
        return '%s-button' % self.name

    @property
    def dateId(self):
        return '%s-date' % self.name

    def __call__(self):
        res = super(CalendarWidget, self).hidden()
        need(RESOURCE_LIBRARY)
        value = self._getFormValue()
        if value is None or value == self.context.missing_value:
            value = ''
        btn = CALENDAR_HTML % {'displayArea': self.dateId,
                               #'button_id': self.buttonId
                               'resource_url': '++resource++images',
                               'value': value
                               }

        src = renderElement('script',
                            type="text/javascript",
                            contents=CALENDAR_SETUP % {'input_id': self.name,
                                                       'displayArea': self.dateId,
                                                       'date': value,
                                                       'button_id': '',
                                                       'format': '%Y-%m-%d',
                                                       'displayformat': '%Y-%m-%d'})
        return "%s%s%s" % (res, btn, src)

    def hasInput(self):
        return ((self.name+".used" in self.request.form)
                or
                (self.name in self.request.form)
                )

class CalendarWidgetHidden(CalendarWidget):
    """Base Class For Search Object Fields"""

    def __call__(self):
        return self.hidden()
