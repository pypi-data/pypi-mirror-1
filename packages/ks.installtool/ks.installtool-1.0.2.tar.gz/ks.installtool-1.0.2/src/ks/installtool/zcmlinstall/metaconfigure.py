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
from zope.component.interfaces import IFactory
from ks.installtool.factory.factory import FactoryBase
from  zope.app.folder.folder import Folder
from ks.installtool import factories

metaconfigure = factories.__dict__
class InstallDirective(object):
    """The "install" directive handler"""

    def __init__(self, _context, root=Folder, factory=None, name="", provides=IFactory, **kw):
        super(InstallDirective, self).__init__(_context, **kw)
        self.kw = kw.copy()
        self._context = _context
        self.name = name
        self.provides = provides
        self.param = {}
        if factory is not None :
            raise TypeError,"Parameter factory is forbidden in this context"

        self.factory = metaconfigure[str(name)] = type(str(name), (FactoryBase,), {
            'root' : root,
            '__module__' : str(factories.__name__),
            'scriptname' : name
            })

    def property(self,context,name="",value="") :
        self.param[name] = value

    def __call__(self) :
        self.factory.context = self.param.copy()
        utility(self._context,
            provides=self.provides,
            factory=self.factory,
            name="%s.%s" % (str(factories.__name__),str(self.name)),
            **self.kw)
