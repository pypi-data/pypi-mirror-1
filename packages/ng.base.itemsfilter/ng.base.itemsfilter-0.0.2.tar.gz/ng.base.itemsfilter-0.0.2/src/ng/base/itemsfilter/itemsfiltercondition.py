### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class for adapter to IItemsFilterCondition

$Id: itemsfiltercondition.py 53280 2009-06-14 11:15:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53280 $"

from zope.interface import implements
from interfaces import IItemsFilterCondition

class ItemsFilterCondition(object) :
    """ Adapter to IItemsFilterCondition. """
    implements(IItemsFilterCondition)
    
    def __init__(self,context) :
        self.context = context

    def __call__(self) :
        return False
                        
                                       
        
