### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

"""RuntimeErrorView class for the Zope 3 based factory package

$Id: runtimeerrorview.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Sergey Shilov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.publisher.browser import BrowserView

class RuntimeErrorView(BrowserView):
    """Вид для отображения ошибки времени выполнения"""
    def getScripts(self):
        """Возвращает список наименований успешно выполненных скриптов"""

        return [item[0] for item in self.context.res]
