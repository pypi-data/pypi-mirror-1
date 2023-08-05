### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter any context to IRegistry interface

$Id: registryadapter.py 49941 2008-02-06 15:18:18Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49941 $"

from zope.interface import Interface
from ng.app.registry.interfaces import IRegistry
from zope.app.zapi import getUtilitiesFor

def RegistryAdapter(context) :
    d = {}
    n = 0
    for name,registry in getUtilitiesFor(IRegistry,context=context) :
        print 1,name,registry

        if name not in d :
            n+=1
            d[name] = (registry,n)
            
        if registry.parent in d :
            del d[registry.parent]            

    if d :
        print d
        di = d.itervalues()
        registry, num = di.next()
        for item, n in di :
            if n < num :
                registry, num = item, n
                
        return registry
        
    raise TypeError                        
    