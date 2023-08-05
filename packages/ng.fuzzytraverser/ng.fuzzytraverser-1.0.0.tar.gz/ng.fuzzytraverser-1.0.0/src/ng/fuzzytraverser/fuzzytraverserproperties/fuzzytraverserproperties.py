### -*- coding: utf-8 -*- #############################################
#######################################################################
# -*- coding: utf-8 -*-
"""The fuzzytraverserproperties class.

$Id: fuzzytraverserproperties.py 13158 2007-11-15 17:04:43Z cray $
"""
__author__  = "ddmitry2 (Dima Khozin)"
__license__ = "GPL"
__version__ = "$Revision: 13158 $"
__date__ = "$Date: 2007-11-15 20:04:43 +0300 (Чтв, 15 Ноя 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from persistent import Persistent
from interfaces import IFuzzyTraverserProperties

class FuzzyTraverserPropertiesBase(object) :
    """ FuzzyTraverserProperties object. It contains some properties """
    implements(IFuzzyTraverserProperties)

    def __init__(self,on=False,rate = 0.5,use=False) :
        self.on = on
        self.rate = 0.5
        self.use = use
        
        
class FuzzyTraverserProperties(FuzzyTraverserPropertiesBase,Persistent): 
    pass       