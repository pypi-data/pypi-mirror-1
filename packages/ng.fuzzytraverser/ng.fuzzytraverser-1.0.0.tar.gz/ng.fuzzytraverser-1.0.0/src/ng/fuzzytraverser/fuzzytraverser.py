### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Fuzzytraverser for the Zope 3

$Id: fuzzytraverser.py 13158 2007-11-15 17:04:43Z cray $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "GPL"
__version__ = "$Revision: 13158 $"
__date__ = "$Date: 2007-11-15 20:04:43 +0300 (Чтв, 15 Ноя 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.publisher.interfaces import NotFound 
from zope.app import zapi 
from zope.app.container.traversal import ContainerTraverser 
import difflib
from interfaces import IFuzzyTraverser
from ng.fuzzytraverser.fuzzytraverserproperties.interfaces import IFuzzyTraverserProperties
from ng.fuzzytraverser.fuzzytraverserannotation.interfaces import fuzzytraverserannotation, fuzzytraverserinfoannotation
from ng.fuzzytraverser.fuzzytraverserproperties.fuzzytraverserproperties import FuzzyTraverserProperties
from ng.fuzzytraverser.fuzzytraverserproperties.fuzzytraverserproperties import FuzzyTraverserPropertiesBase
from ng.fuzzytraverser.fuzzytraverserinfo.fuzzytraverserinfo import FuzzyTraverserInfo


class FuzzyTraverser(ContainerTraverser):
    """Traverses an container items"""
   
    __used_for__ = IFuzzyTraverser
    nmax = None

    def __init__(self,*kv,**kw) :
        print 11
        print kv,kw
        super(FuzzyTraverser,self).__init__(*kv,**kw)
        print 12
        
    
    def publishTraverse(self, request, name): 
        """See zope.publisher.interfaces.browser.IBrowserPublisher""" 
        self.info = request.annotations.setdefault(fuzzytraverserinfoannotation,[])
        subob = self.get(name) 
        if subob is not None: 
            return subob 
        return super(FuzzyTraverser, self).publishTraverse(request, name)

    def get(self,name) :
        """Try to fuzzy get"""

        res = self.context.get(name,None)        
        if res is None :
            cfg = FuzzyTraverserPropertiesBase(on=True)
            
            try :
                cfg = zapi.getUtility(IFuzzyTraverserProperties,context=self.context)
            except LookupError,msg :
                print "Fuzzy Property utility not found:",msg
        
            if self.request.annotations.has_key(fuzzytraverserannotation) :
                cfg = self.request.annotations[fuzzytraverserannotation]


            try:
                annotation = IFuzzyTraverserProperties(self.context)
            except TypeError,msg:
                print "Except:",msg
            else :
                if annotation.use :
                    cfg = self.request.annotations[fuzzytraverserannotation] = annotation 

            if cfg.on :
                imax = cfg.rate
                nmax = None

                for key in self.context.keys() :
                    i = difflib.SequenceMatcher(None,name,key).ratio()
                    if i >= imax :
                        imax = i
                        nmax = key
                if nmax :
                    self.info.append(FuzzyTraverserInfo(imax=imax,name=nmax,orig=name))
                    return self.context.get(nmax,None)

                return self.context.get(nmax,None)                    
        
        return res