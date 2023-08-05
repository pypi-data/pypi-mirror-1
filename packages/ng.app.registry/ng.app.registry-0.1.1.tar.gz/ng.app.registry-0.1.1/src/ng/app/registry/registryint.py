### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registryInt.py 48862 2007-12-14 19:47:14Z rt $
"""
__author__  = "SergeyAlembekov,2007"
__license__ = "GPL"
__version__ = "$Revision: 48862 $"


from zope.interface import implements
from zope.schema import Int
from interfaces import IRegistryInt,IRegistryContent
from persistent import Persistent
from zope.app.container.contained import Contained

class RegistryInt(Persistent,Contained):
    __doc__ = IRegistryInt.__doc__
    implements(IRegistryInt,IRegistryContent)
    # See registry.interfaces.IRegistryInt
    title = None
    factory = Int
    data = 0
    