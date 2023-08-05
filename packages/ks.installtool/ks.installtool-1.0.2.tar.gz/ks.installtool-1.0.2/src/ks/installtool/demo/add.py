### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""AddMixIn class for the Zope 3 based installtool package

$Id: add.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = ""
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from installtool.installscript.interfaces import IInstallScript

class AddMixIn(object) :

    def create(self,*args, **kw):
        print "MyCreate!!"
        self._my_factory = self._factory
        print self._my_factory
        return self._my_factory(self,*args, **kw)

    def add(self, content):
        print "MyAdd!!!"
        content = super(AddMixIn,self).add(content)
        print "RunScripts!!!"
        self._my_factory.runScripts(content)
        print "Ready!!"
        return content
