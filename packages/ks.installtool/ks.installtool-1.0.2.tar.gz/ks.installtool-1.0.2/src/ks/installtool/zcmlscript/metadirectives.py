### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interface of ZCML metadirective "zcml:install"

$Id: metadirectives.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Sergey Shilov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface
from zope.component.zcml import IUtilityDirective
from zope.schema import Text
from zope.configuration.fields import GlobalObject, GlobalInterface, Tokens
from ks.installtool.zcmlinstall.metadirectives import IPropertySubdirective
from zope.schema import Text, TextLine, Field, Bool, Datetime


class IScriptDirective(IUtilityDirective):
    """The "Script" directive interface"""

    script = GlobalObject(title=u"Script", required=False)

    requires = Tokens(title=u"RequiredName", value_type=Text())

    name = TextLine(title=u"ScriptName")

    factory = TextLine(title=u"FactoryName")
