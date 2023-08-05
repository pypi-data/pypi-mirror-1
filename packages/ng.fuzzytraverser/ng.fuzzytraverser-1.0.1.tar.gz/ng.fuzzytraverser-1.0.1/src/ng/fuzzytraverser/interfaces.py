### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Marker interface for the  Zope 3 based fuzzytraverser package

$Id: interfaces.py 13150 2007-11-15 14:11:31Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
 
from zope.app.container.interfaces import ISimpleReadContainer, IItemContainer
class IFuzzyTraverser(ISimpleReadContainer): 
  """Marker for folders whose contained items keys are fuzzy.""" 
  