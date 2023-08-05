### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registryTextLine.py 48862 2007-12-14 19:47:14Z rt $
"""
__author__  = "SergeyAlembekov,2007"
__license__ = "GPL"
__version__ = "$Revision: 48862 $"


from zope.interface import implements
from zope.schema import TextLine
from interfaces import IRegistryTextLine, IRegistryContent
from persistent import Persistent
from zope.app.container.contained import Contained

class RegistryTextLine(Persistent,Contained):
    __doc__ = IRegistryTextLine.__doc__
    implements(IRegistryTextLine,IRegistryContent)
    # See registry.interfaces.IRegistryTextline
    title = None
    factory = TextLine
    data=u""
