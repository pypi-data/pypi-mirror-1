### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based fuzzytraverserannotations package

$Id: interfaces.py 13158 2007-11-15 17:04:43Z cray $
"""
__author__  = "Arvid"
__license__ = "GPL"
__version__ = "$Revision: 13158 $"
__date__ = "$Date: 2007-11-15 20:04:43 +0300 (Чтв, 15 Ноя 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""
 
from zope.interface import Interface

class IFuzzyTraverserAnnotable(Interface):
    """ A fuzzytraverserannotable object. If object have got this interface,
    object can have annotations with fuzzytraverser parameters """
    
fuzzytraverserannotation     = "ng.fuzzytraverserproperties.FuzzyTraverserProperties"
fuzzytraverserinfoannotation = "ng.fuzzytraverserproperties.FuzzyTraverserInformation"
    