### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Information interface to save statistic on get

$Id: interfaces.py 13149 2007-11-15 13:59:56Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"

from zope.interface import Interface
from zope.schema import Float, TextLine

class IFuzzyTraverserInfo(Interface):
    """ A fuzzytraverserproperties object """
    
    imax = Float(
        title=u"Maximal derivation",
        required=True)

    origname = TextLine(
        title=u"Original name",
        required=True)

    realname = TextLine(
        title=u"Real name",
        required=True)




