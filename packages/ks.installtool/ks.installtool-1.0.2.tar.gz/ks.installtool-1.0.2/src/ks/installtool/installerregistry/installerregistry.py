### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ReferenceBase class for the Zope 3 based installerregistrye package

$Id: installerregistry.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov, 2007 02 14"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface,implements
from interfaces import IInstallerRegistry

class InstallerRegistry(object) :
    implements(IInstallerRegistry)

    def __init__(self) :
        self._registry = {}

    def registerScript(self,script,factory) :
        """ Register script for factory """
        self._registry.setdefault(factory,[]).append(script)

    def queryScript(self,factory) :
        """ Return all scripts for this factory """
        return (x for x in self._registry[factory])



