### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
######################################################################

"""Factory class for the Zope 3 based installtool package

$Id: factory.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__  = "ZPL"
__version__ = "$Revision: 35334 $"
__date__    = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.interface import Interface
from zope.app.zapi import getSiteManager
from ks.lib.topolsort import topSort, SortIsNotPossible, UnknownDependency
from zope.interface import implements,implementedBy
from zope.component.interfaces import IFactory
from ks.installtool.installerregistry.interfaces import IInstallerRegistry
from ks.installtool.exceptions import ScriptError, UnresolvedDepsError, UnknownDependencyError
from logging import getLogger

logger = getLogger('installtool')

from ks.installtool.interfaces import _

class FactoryBase(object) :
    implements(IFactory)

    root = lambda x : None
    scriptname = ""
    context = {}

    def __call__(self,*kv,**kw) :
        self.ob = self.root()
        self.context.update(kw)
        #self.runScripts()
        return self.ob

    def getInterfaces(self,*kv,**kw) :
        return implementedBy(self.root)

    def getScripts(self):
        """Return script records, registered for factory """

        return topSort(
            [ob \
                for ob in \
                    getSiteManager().getUtility(IInstallerRegistry) \
                        .queryScript(self.scriptname) \
                ]
        )

    def runScripts(self,ob):
        """Run scripts in factory context """
        res = []
        try:
            for script in self.getScripts() :
                try:
                    res.append((script.name,script(self.ob,self.context)))
                except Exception,msg:
                    logger.error('FactoryBase.runScripts', exc_info=True)
                    raise ScriptError(script.name,msg,res)
        except SortIsNotPossible, details:
            logger.error("Can't resolve dependencies: %(details)s", dict(details=details), exc_info=True)
            raise UnresolvedDepsError(details)
        except UnknownDependency, details:
            logger.error('UnknownDependency: %(details)s', dict(details=details), exc_info=True)
            raise UnknownDependencyError(details[0])
        return res
