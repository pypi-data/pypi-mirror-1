### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based fuzzytraverserannotations package

$Id: interfaces.py 13147 2007-11-15 13:18:47Z cray $
"""
__author__  = "Arvid"
__license__ = "GPL"
__version__ = "$Revision: 13147 $"
__date__ = "$Date: 2007-11-15 16:18:47 +0300 (Чтв, 15 Ноя 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""
 
from zope.interface import Interface

class IFuzzyTraverserAnnotable(Interface):
    """ A fuzzytraverserannotable object. If object have got this interface,
    object can have annotations with fuzzytraverser parameters """
    
fuzzytraverserannotation     = "ng.fuzzytraverserproperties.FuzzyTraverserProperties"
fuzzytraverserinfoannotation = "ng.fuzzytraverserproperties.FuzzyTraverserInformation"
    