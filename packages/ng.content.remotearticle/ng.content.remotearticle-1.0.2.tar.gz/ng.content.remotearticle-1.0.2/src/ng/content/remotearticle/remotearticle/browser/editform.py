### -*- coding: utf-8 -*- #############################################
#######################################################################
"""EditForm mix-in for edit page of Zope 3 based ng.content.article package

$Id: editform.py 52024 2008-11-14 09:59:13Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52024 $"

from zope.interface import Interface
from cachedconvertor.object2psadapter.interfaces import IPropertySheet      
from zope.app.form.utility import setUpEditWidgets
from zope.security.proxy import removeSecurityProxy

class Proxy(object) :
    def __init__(self,adapted,**kw) :
        self.adapted = removeSecurityProxy(adapted)
        print 'adapted', self.adapted
        self.kw = kw
        
    def __getattr__(self,name) :
        print "get",name
        if name in [ "kw","adapted" ] :
            return self.__dict__[name]
        try :
            return self.kw[name]
        except KeyError :
            print "get2",name
            return getattr(self.adapted,name)

    def __setattr__(self,name,value) :
        print "set:",name,value
        if name in ["kw","adapted"] :
            self.__dict__[name] = value
            return
        return setattr(self.adapted,name,value)
            
class EditFormView(object) :

    def _setUpWidgets(self):
        self.adapted = Proxy(self.schema(self.context),body=IPropertySheet(self.context)['body'])
        setUpEditWidgets(self, self.schema, source=self.adapted, names=self.fieldNames)


        
        
        
