### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registryTextLine.py 48862 2007-12-14 19:47:14Z rt $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 48862 $"


from zope.interface import implements
from zope.schema import Text
from interfaces import IRegistryText, IRegistryContent
from persistent import Persistent
from zope.app.container.contained import Contained

class RegistryText(Persistent,Contained):
    __doc__ = IRegistryText.__doc__
    implements(IRegistryText,IRegistryContent)
    # See registry.interfaces.IRegistryText
    title = None
    factory = Text
    data=u""
