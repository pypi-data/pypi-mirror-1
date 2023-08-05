### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

"""Interfaces for the Zope 3 based installscript package

$Id: interfaces.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__  = "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, Datetime
from ks.installtool.interfaces import _

class IInstallScript(Interface) :

    name = TextLine(title=_(u"Name"), required=False)

    requires = Field()

    script = Field()
