# -*- coding: utf-8 -*-

"""The fuzzytraverserproperties interface

Interfaces for the Zope 3 based fuzzytraverserproperties package

$Id: interfaces.py 13158 2007-11-15 17:04:43Z cray $
"""
__author__  = "ddmitry2 (Dima Khozin)"
__license__ = "GPL"
__version__ = "$Revision: 13158 $"
__date__ = "$Date: 2007-11-15 20:04:43 +0300 (Чтв, 15 Ноя 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""
 
from zope.interface import Interface
from zope.schema import Float, Field, Bool
from zope.app.container.interfaces import IContained, IContainer

class IFuzzyTraverserProperties(Interface):
    """ A fuzzytraverserproperties object """
    # XXX Впишите докстринг
    
    on = Bool(
        title=u"On",
        description=u"On",
        default=False,
        required=True)

    use = Bool(
        title=u"Use this parameters",
        default=False,
        required=True)
    
    rate = Float(
        title=u"Порог срабатывания",
        description=u"this is a raid",
        default=0.5,
        required=True)


