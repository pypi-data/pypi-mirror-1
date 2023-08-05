### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registrynamespace.py 49088 2007-12-29 23:27:21Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49088 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.file.image import Image
from zope.traversing.interfaces import ITraverser, ITraversable
from zope.app.catalog.interfaces import ICatalog
from ng.app.registry.interfaces import IRegistry
from zope.app.zapi import getUtilitiesFor

from zope.app.zapi import getUtility

class RegistryNamespace(object) :
    implements(ITraversable)

    def __init__(self,context,request) :
        self.context = context
        self.request = request

    def traverse(self,name,ignored) :
        nm = name.split(':',1)
        try:
            return IRegistry(self.context).param(*nm)
        except TypeError,msg:
            try :
                return nm[1]
            except IndexError :
                return ignored
