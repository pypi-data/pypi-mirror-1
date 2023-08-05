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
__author__  = ""
__license__    = "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

from ks.installtool.interfaces import _

class IDemo(Interface) :

    #title=TextLine(title=u"Title")

    body=Text(title=_(u"Body"))

    back_email=TextLine(title=_(u'Your e-mail'), default=u'someone@somewhere.com')
