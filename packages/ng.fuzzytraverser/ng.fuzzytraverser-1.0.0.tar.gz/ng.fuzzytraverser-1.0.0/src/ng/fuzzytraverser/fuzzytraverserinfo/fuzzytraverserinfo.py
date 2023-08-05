### -*- coding: utf-8 -*- #############################################
#######################################################################
# -*- coding: utf-8 -*-
"""The fuzzytraverserproperties class.

$Id: fuzzytraverserinfo.py 13158 2007-11-15 17:04:43Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from persistent import Persistent
from interfaces import IFuzzyTraverserInfo

class FuzzyTraverserInfo(object) :
    """ FuzzyTraverserInfo object. It contains some statistic about traverse"""
    implements(IFuzzyTraverserInfo)

    def __init__(self,imax,name,orig) :
        self.imax = imax
        self.name = name
        self.orig = orig
        
        
        
