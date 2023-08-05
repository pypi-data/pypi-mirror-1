### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Sample scripts class for the Zope 3 based installtool package

$Id: scripts.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Andrey Orlov"
__license__	= "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"


from zope.app.folder.folder import Folder

def scriptA(context,**kw) :
    print "A:",context,kw
    for i in xrange(0,20) :
        print "Create folder",i
        context["name%03i" % i] = Folder()

    return "OK"

def scriptB(context,**kw) :
    print "B:",context,kw
    return "OK"

def scriptC(context,**kw) :
    print "C:",context,kw
    return "OK"

def scriptD(context,**kw) :
    print "D:",context,kw
    return "OK"

def scriptE(context,**kw) :
    print "E:",context,kw
    return "OK"


