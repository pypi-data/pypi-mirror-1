### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: registry.py 49518 2008-01-16 21:37:16Z cray $
"""
__author__  = "SergeyAlembekov,2007"
__license__ = "GPL"
__version__ = "$Revision: 49518 $"

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
			res = queryUtility(IRegistry, name=self.parent, context=self, default=None)
			if res is not None:
				return res.param(name, default)
			return default



