### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Vocabulary for the Zope 3 based product package

$Id: interfaces.py 49026 2007-12-26 02:30:55Z rt $
"""
__author__  = "SergeyAlembekov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49026 $"

from zope.schema.vocabulary import SimpleVocabulary
from zope.app.zapi import getUtilitiesFor
from interfaces import IRegistry

def RegistryVocabulary(context):
    # Нужно возвращать _словарь_ это же фабрика словарей, верно?
    # А ты возвращал список значений.
	return SimpleVocabulary.fromValues([x for x,y in getUtilitiesFor(IRegistry)])
