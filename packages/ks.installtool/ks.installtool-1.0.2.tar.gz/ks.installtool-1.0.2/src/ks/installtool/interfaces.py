### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Sergey Shilov"
__license__  = "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface
from zope.schema import TextLine, Field

import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('ks.installtool')

class IScriptError(Interface):

    script = TextLine(title=_(u'Script name'), required=False)

    msg = TextLine(title=_(u'Error message'), required=False)

    res = Field()

class IUnresolvedDepsError(Interface):
    """Интерфейс для исключения, возбуждаемого при невозможности разрешить
    зависимости. Имеет дополнительный параметр res, содержащий список скриптов
    для которых не удалось разрешить зависимости."""

    res = Field()

class IUnknownDependencyError(Interface):
    """Интерфейс для исключения, возбуждаемого при нахождении несуществующей
    зависимости. Имеет дополнительные параметр msg содержащие сообщение об
    имени скрипта, содержащего неизвестную зависимость и имени этой
    зависимости."""

    msg = TextLine(title=_(u'Error message'), required=False)
