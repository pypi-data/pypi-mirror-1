### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

# Make it a Python package

import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('ks')

from object.objectdisplaywidget import ObjectDisplayWidget
from selectdate.selectdatewidget import SelectDateWidget, SelectDatetimeWidget
from html.htmldisplaywidget import UnicodeHTMLDisplayWidget, HTMLDisplayWidget
from html.htmlinputwidget import HTMLInputWidget
from smarturi.smarturiwidget import SmartURIWidget, SmartURIDisplayWidget
from captcha.captchawidget import CaptchaWidget
from image.imagedisplaywidget import ImageDisplayWidget
from repeat.repeatwidget import PasswordRepeatWidget
from re.rewidget import EmailWidget, NameWidget, WidgetREBase
from externalurl.externalurlwidget import ExternalURLWidget, ExternalURLsWidget
from ks.smartimage.smartimageschema.smartimagewidget import SmartImageWidget
from ks.smartimage.smartimageschema.smartimagedisplaywidget import SmartImageDisplayWidget
from directfileupload.directfileuploadwidget import DirectFileUploadWidget
