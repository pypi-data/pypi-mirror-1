### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ZCML factoryform directive handler

$Id: metaconfigure.py 35334 2008-01-25 14:33:40Z cray $
"""
__author__  = "Sergey Shilov"
__license__  = "ZPL"
__version__ = "$Revision: 35334 $"
__date__ = "$Date: 2008-01-25 17:33:40 +0300 (Птн, 25 Янв 2008) $"

from zope.component.zcml import utility
from zope.component.interfaces import IFactory
from ks.installtool.factory.factory import FactoryBase
from  zope.app.folder.folder import Folder
from ks.installtool import factories
from ks.installtool.zcmlinstall.metaconfigure import InstallDirective
from zope.app.component.contentdirective import ClassDirective
from zope.app.form.browser.metaconfigure import AddFormDirective
from zope.schema import getFieldNames
from zope.app.publisher.browser.menumeta import addMenuItem
from add import AddMixIn

metaconfigure = factories.__dict__

class FactoryFormDirective(InstallDirective):
    """The "factoryform" directive handler"""

    def __init__(self, _context, root=Folder, factory=None, name="",
                 provides=None, class_=None, fields=None,
                 schema=None, for_=None, permission=None, view='', title='',
                 description='', **kw):

        super(FactoryFormDirective, self).__init__(_context, root=root,
             name=name, provides=IFactory, **kw)

        if factory is not None :
            raise ValueError,"factory must be None in this context"

        if provides is not None :
            raise ValueError,"provides must be None in this context"

        self.schema = schema
        self.for_ = for_
        self.permission = permission
        self.view = view
        self.title = title
        self.description = description
        self.fields = fields

        if class_:
            self.class_ = type(class_, AddMixIn, {})
        else:
            self.class_ = AddMixIn
            
        self.addform =  AddFormDirective(self._context, name=self.view,
            content_factory_id=str("ks.installtool.factories.%s" % self.name), schema=self.schema,
            class_=self.class_, permission=self.permission,
            keyword_arguments=self.fields is None and getFieldNames(self.schema)
                                               or tuple(set(self.fields).intersection(set(getFieldNames(self.schema)))),
            for_=self.for_, fields = self.fields)


    def widget(self, _context, field, **kw) :
        return self.addform.widget(_context, field, **kw)

    def __call__(self) :
        super(FactoryFormDirective, self).__call__()

        obj = ClassDirective(self._context, self.factory)
        obj.require(self._context, permission=self.permission, interface=[IFactory,])
        obj()

        self.addform()

        addMenuItem(self._context,
            title = self.title, description=self.description,
            factory=str("ks.installtool.factories.%s" % self.name),
            view=self.view,
            permission=self.permission)
