### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based captcha package

$Id: interfaces.py 35228 2007-11-28 10:54:43Z anton $
"""
__author__  = ""
__license__ = "<undefined>" # необходимо согласование
__version__ = "$Revision: 35228 $"
__date__ = "$Date: 2007-11-28 12:54:43 +0200 (Wed, 28 Nov 2007) $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Int
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint


class ICaptcha(Interface) :

    width = Int(
        title = u"Image width",
        description = u"",
        min = 0,
        max = 1280,
        default = 100
        )

    height = Int(
        title = u"Image height",
        description = u"",
        min = 0,
        max = 1024,
        default = 100
        )

    noise = Int(
        title = u"Noise level",
        description = u"",
        min = 0,
        max = 100,
        default = 20
        )

    secret = Int(
        title = u"Shared Secret",
        description = u"",
        default = 05555
        )

    fontsize = Int(
        title = u"Font Size",
        description = u"",
        default = 20
        )

    font = TextLine(
        title = u"Full path to truetype Font",
        description = u"",
        default = u'verdanai.ttf'
        )

    mode = TextLine(
        title = u"Image mode",
        description = u"",
        default = u'RGB'
        )

    format = TextLine(
        title = u"Image format",
        description = u"",
        default = u'PNG'
        )

    mimetype = TextLine(
        title = u"MimeType",
        description = u"",
        default = u'image/png'
        )

    min = Int(
        title = u"Minimal Key",
        description = u"",
        default = 1000
        )

    max = Int(
        title = u"Maximum Key",
        description = u"",
        default = 9999
        )

    interval = Int(
        title = u"Key lifetime",
        description = u"",
        min = 600,
        max = 7200,
        default = 3600
        )

    def banner(key) :
        """ Генерирует картинку, на которой изображён указанный в параметре key
            (слово, набор цифр или нечто подобное)
        """

    def decrypt(key) :
        """ Принимает ключ в зашифрованном виде, расшифровывает его и
            возвращает результат расшифровки
        """

    def check(key, x) :
        """ Проверяет, соответствуют ли данные, введённые пользователем,
            данным, изображённым на картинке
        """

    def getkey(self):
        """ Получает случайный ключ
        """
