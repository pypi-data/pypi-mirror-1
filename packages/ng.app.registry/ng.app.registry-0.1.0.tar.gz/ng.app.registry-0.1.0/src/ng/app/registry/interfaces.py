### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49342 2008-01-10 18:07:48Z rt $
"""
__author__  = "SergeyAlembekov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49342 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Int, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.zapi import getUtility

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

class IRegistry(Interface):
	"""A registry object"""

	parent = Choice(
		vocabulary='RegistryVocabulary',
		title=u"Parent",
		required=False)
	
	def param(name, default):
		""" Return from container value of name """

class IRegistryContent(Interface):
	""" Iterface that specify permission of object that can be content
                of notebook """

        __parent__ = Field(constraint = ContainerTypesConstraint(IRegistry))
	

class IRegistryContainer(IContainer, IRegistry):
	"""Registry Container"""

	def __setitem__(name, object):
		pass

	__setitem__.precondition = ItemTypePrecondition(IRegistryContent)



