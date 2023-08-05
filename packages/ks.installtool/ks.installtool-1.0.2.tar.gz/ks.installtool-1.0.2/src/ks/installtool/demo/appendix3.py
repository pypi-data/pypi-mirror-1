### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Sample scripts class for the Zope 3 based installtool package

$Id: appendix3.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"


from zope.app.folder.folder import Folder
from zope.dublincore.interfaces import IZopeDublinCore

def scriptAppendix3(context, **kw) :

    schema = {
        u"a/d/e" : u"Название ade",
        u"a/b/c" : u"Название abc",
        u"a/b"   : u"Название ab",
        u"a/a"   : u"Название aa",
        u"a"     : u"Название a",
    }

    for path in sorted(schema.keys()) :
        items = path.split("/")
        end = items[-1]
        ob = context
        for item in items[0:-1]:
            try :
                ob = ob[item]
            except KeyError :
                ob[item] = Folder()
                ob = ob[item]
        ob[end] = Folder()
        IZopeDublinCore(ob[end]).title = schema[path]

    return "Ok"
