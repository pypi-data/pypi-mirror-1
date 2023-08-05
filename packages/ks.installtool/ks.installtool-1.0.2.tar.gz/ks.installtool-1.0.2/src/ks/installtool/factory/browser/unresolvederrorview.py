### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

"""UnresolvedErrorView class for the Zope 3 based factory package

$Id: unresolvederrorview.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Sergey Shilov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.publisher.browser import BrowserView

class UnresolvedErrorView(BrowserView):
    """Вид для отображения ошибки невозможности разрешения зависимостей"""
    def getScripts(self):
        """Возвращает список кортежей, где первый элемент - имя скрипта, а
        второй - список его зависимостей"""
        return [(obj.name, obj.requires) for obj in self.context.res[0]]
