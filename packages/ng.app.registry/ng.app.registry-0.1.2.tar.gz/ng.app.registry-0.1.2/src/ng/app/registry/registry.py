### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registry.py 50798 2008-02-21 11:05:27Z cray $
"""
__author__  = "SergeyAlembekov,2007"
__license__ = "GPL"
__version__ = "$Revision: 50798 $"

from zope.interface import implements
from interfaces import IRegistryContainer
from interfaces import IRegistry
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IContainer
from zope.app.zapi import queryUtility

class Registry(BTreeContainer):
    __doc__ = IRegistryContainer.__doc__
    implements(IRegistryContainer, IRegistry)
    parent=None

    def param(self, name, default):
        try:
            return self[name].data
        except LookupError:
            if self.parent :
                res = queryUtility(IRegistry, name=self.parent, context=self, default=None)
                if res is not None:
                    return res.param(name, default)
            return default

    def export(self,ob,*kv) :
        for name in kv :
            setattr(ob,name,self.param(name,getattr(ob,name)))