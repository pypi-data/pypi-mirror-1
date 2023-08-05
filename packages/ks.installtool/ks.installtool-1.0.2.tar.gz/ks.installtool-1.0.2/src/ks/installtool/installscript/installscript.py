### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""InsltallScript class for the Zope 3 based installtool package

$Id: installscript.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = ""
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ks.installtool.installscript.interfaces import IInstallScript

class InstallScript(object) :
    implements(IInstallScript)

    name = ""
    requires = []
    script = None
    context = {}

    def __init__(self, name, requires, script) :
        self.name = name
        self.requires = requires
        self.script = script
        self.context = {}

    def __call__(self, context, properties) :
        return self.script(context,**dict(((str(x),y) for x,y in properties.items())) )

