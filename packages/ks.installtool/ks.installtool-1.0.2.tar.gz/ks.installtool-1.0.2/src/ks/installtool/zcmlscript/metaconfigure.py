### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ZCML Install directive handler

$Id: metaconfigure.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.component.zcml import utility
from ks.installtool.installscript.interfaces import IInstallScript
from ks.installtool.installscript.installscript import InstallScript
from ks.installtool import registry

class ScriptDirective(object):
    """The "install" directive handler"""

    def __init__(self, _context, factory="", name="", requires=[], script=None):
        self._context = _context
        self.factory = factory
        self.script = InstallScript(name,requires,script)

    def property(self,context,name="",value="") :
        self.script.context[name] = value

    def __call__(self) :
        registry.registerScript(self.script, self.factory)
