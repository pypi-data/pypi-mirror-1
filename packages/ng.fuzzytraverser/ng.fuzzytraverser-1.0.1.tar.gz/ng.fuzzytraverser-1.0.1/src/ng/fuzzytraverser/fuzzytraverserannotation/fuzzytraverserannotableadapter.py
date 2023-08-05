### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The fuzzytraverserannotations class.

$Id: fuzzytraverserannotableadapter.py 13147 2007-11-15 13:18:47Z cray $
"""
__author__  = "Arvid"
__license__ = "GPL"
__version__ = "$Revision: 13147 $"
__date__ = "$Date: 2007-11-15 16:18:47 +0300 (Чтв, 15 Ноя 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from ng.fuzzytraverser.fuzzytraverserproperties.interfaces import IFuzzyTraverserProperties
from ng.fuzzytraverser.fuzzytraverserproperties.fuzzytraverserproperties import FuzzyTraverserProperties

from zope.annotation.interfaces import IAnnotations

from interfaces import fuzzytraverserannotation

def FuzzyTraverserAnnotableAdapter(context):
    return IAnnotations(context).setdefault(fuzzytraverserannotation,  FuzzyTraverserProperties())
    