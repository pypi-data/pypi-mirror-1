### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registryedit.py 50798 2008-02-21 11:05:27Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50798 $"

from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.interface import implements,implementedBy
from zope.security.proxy import removeSecurityProxy
from zope.schema import getFieldsInOrder, getFieldNames

class RegistryEdit(object) :
    def __init__(self,context,request) :
        schema = InterfaceClass('IRegistryForm',(Interface,),
            dict( [ (x,removeSecurityProxy(y.factory)(title=unicode(x),default=y.data)) for x,y in context.items()  ] )
        )

        self.schema = schema
        self.fieldNames = getFieldNames(schema)
        super(RegistryEdit,self).__init__(context,request)


        
    def getData(self,*kv,**kw) :
        return dict( [ (name,x.data) for name,x in self.context.items() ] )
        
    def setData(self,d,**kw) :
        for key,value in d.items() :
            self.context[key].data = value        
        return True
                    