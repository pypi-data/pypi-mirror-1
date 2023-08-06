### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.base.itemsfilter package

$Id: interfaces.py 53280 2009-06-14 11:15:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53280 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IReadContainer
                
                
class IItemsFilter(Interface) :

    def __getitem__(name) :
        """Return filter by name """
                            
class IItemsFilterAble(Interface) :
    """ """

class IItemsFilterRecord(IReadContainer) :
    """ """

class IItemsFilterCondition(Interface) :
    """ """
    