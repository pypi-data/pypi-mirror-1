### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Image checker view  for the Zope 3 imageechecker package

$Id: captchaview.py 35230 2007-11-28 11:21:54Z anton $
"""
__author__  = "Egor Shershenev"
__license__ = "ZPL"
__version__ = "$Revision: 35230 $"
__date__ = "$Date: 2007-11-28 13:21:54 +0200 (Wed, 28 Nov 2007) $"

from zope.publisher.browser import BrowserView
from zope.component import getUtility
from ks.captcha.interfaces import ICaptcha

class CaptchaView(BrowserView):

    def banner(self) :
        ic = getUtility(ICaptcha,context=self.context)
        self.request.response.setHeader("Content-Type","image/jpeg")
        return ic.banner(self.request.get('key'))
