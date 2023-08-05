### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: fuzzytraverserannotableedit.py 13158 2007-11-15 17:04:43Z cray $
"""
__author__  = "Arvid"
__license__ = "GPL"
__version__ = "$Revision: 13158 $"

from zope.schema import getFieldNames 
from zope.app.folder.interfaces import IFolder
from ng.fuzzytraverser.fuzzytraverserproperties.interfaces import IFuzzyTraverserProperties

class FuzzyTraverserAnnotableEdit(object) :
    def getData(self,*kv,**kw) :
        self.fa = IFuzzyTraverserProperties(self.context)
        return [ (x,getattr(self.fa,x)) for x in  getFieldNames(IFuzzyTraverserProperties)]

    def setData(self,d,**kw) :
        for x in getFieldNames(IFuzzyTraverserProperties) :
            setattr(self.fa,x,d[x])
        return True
        
