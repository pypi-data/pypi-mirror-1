### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ObjectDisplayWidget class for the Zope 3 based ks.widget package

$Id: objectdisplaywidget.py 35321 2008-01-07 22:03:46Z cray $
"""

__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35321 $"
__date__ = "$Date: 2008-01-08 00:03:46 +0200 (Tue, 08 Jan 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from zope.interface import implements
from zope.schema import getFieldNamesInOrder

from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.utility import setUpWidgets
from zope.app.form.browser.widget import DisplayWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

# from ks.widget import _ не используется

class ObjectDisplayWidgetView(object):

    template = ViewPageTemplateFile('objectdisplaywidget.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()


class ObjectDisplayWidget(DisplayWidget):

    implements (IDisplayWidget)

    names = None

    viewFactory = ObjectDisplayWidgetView

    def __init__(self, context, request, **kw):
        super(ObjectDisplayWidget, self).__init__(context, request)

        # define view that renders the widget
        self.view = self.viewFactory(self, request)

        # handle foo_widget specs being passed in
        if self.names is None:
            self.names = getFieldNamesInOrder(self.context.schema)
        for k, v in kw.items():
            if k.endswith('_widget'):
                setattr(self, k, v)

        # set up my subwidgets
        self._setUpWidgets()


    def setPrefix(self, prefix):
        super(ObjectDisplayWidget, self).setPrefix(prefix)
        # XXX: is this really needed for display widgets?
        self._setUpWidgets()

    def _setUpWidgets(self):
        # subwidgets need a new name
        setUpWidgets(self, self.context.schema, IDisplayWidget,
                         prefix=self.name, names=self.names,
                         context=self.context)

    def __call__(self):
        return self.view()

    def legendTitle(self):
        return self.context.title or self.context.__name__

    def getSubWidget(self, name):
        return getattr(self, '%s_widget' % name)

    def subwidgets(self):
        return [self.getSubWidget(name) for name in self.names]

    def hidden(self):
        """Render the object as hidden fields."""
        result = []
        for name in self.names:
            result.append(getSubwidget(name).hidden())
        return "".join(result)

    def setRenderedValue(self, value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
        # re-call setupwidgets with the content
        self._setUpWidgets()
        for name in self.names:
            self.getSubWidget(name).setRenderedValue(getattr(value, name, None))
