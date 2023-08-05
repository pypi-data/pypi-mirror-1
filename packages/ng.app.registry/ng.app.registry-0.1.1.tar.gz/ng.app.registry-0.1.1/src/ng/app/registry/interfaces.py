### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id$
"""
__author__  = "SergeyAlembekov, 2007"
__license__ = "GPL"
__version__ = "$Revision$"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Int, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.zapi import getUtility
from zope.app.keyreference.interfaces import IKeyReference

class IRegistryTextLine(Interface):
    data = TextLine(
            title = u'Value of textual parameter',
            description = u'',
            default = u'',
            required = False)
                            
class IRegistryInt(Interface):
    data = Int(
        title = u'Value of int parameter',
        description = u'',
        default = 0,
        required = False)

def check_id(name, check_list=set()) :
    if name is None :
        return True
    else :   
        ob = getUtility(IRegistry, name=name)
        iob=IKeyReference(ob)
        if iob in check_list :
            return False
        else :
            return check_id(ob.parent, check_list | set([iob]))

class SafeChoice(Choice):
    def constraint(self, name):
        return check_id(name, set([IKeyReference(self.context)]))

class IRegistry(Interface):
    """A registry object"""

    parent = SafeChoice(
        vocabulary='RegistryVocabulary',
        title=u"Parent",
        required=False)
    
    def param(name, default):
        """ Return from container value of name """

    def export(ob, *names) :
        """ Set attributes enumerated by names equal by values from registry """

class IRegistryContent(Interface):
    """ Iterface that specify permission of object that can be content
        of registry """

    __parent__ = Field(constraint = ContainerTypesConstraint(IRegistry))
    

class IRegistryContainer(IContainer, IRegistry):
    """Registry Container"""

    def __setitem__(name, object):
        pass

    __setitem__.precondition = ItemTypePrecondition(IRegistryContent)



