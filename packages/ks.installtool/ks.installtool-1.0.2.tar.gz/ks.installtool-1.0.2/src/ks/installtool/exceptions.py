### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
######################################################################
"""Exception classes for the Zope 3 based installtool package

$Id: exceptions.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__    = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import implements
from interfaces import IScriptError, IUnresolvedDepsError, IUnknownDependencyError

class ScriptError(Exception) :
    implements(IScriptError)

    def __init__(self,script,msg,res) :
        Exception.__init__(self,script,msg,res)
        self.script = script
        self.msg = msg
        self.res = res

class UnresolvedDepsError(Exception) :
    implements(IUnresolvedDepsError)

    def __init__(self, res) :
        Exception.__init__(self, res)
        self.res = res

class UnknownDependencyError(Exception) :
    implements(IUnknownDependencyError)

    def __init__(self, msg) :
        #Exception.__init__(self, msg,res)
        Exception.__init__(self, msg)
        self.msg = msg

