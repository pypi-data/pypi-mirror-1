### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based installerregistry package

$Id$
"""
__author__  = "Andrey Orlov, 2007 02 14"
__license__	= "ZPL"
__version__ = "$Revision$"
__date__ = "$Date$"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime

class IInstallerRegistry(Interface) :

    def registerScript(script,factory) :
        """ Register script for factory """

    def queryScript(factory) :
        """ Return all scripts for this factory """


