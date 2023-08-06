### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter used to access to items filter

$Id: itemsfilter.py 53280 2009-06-14 11:15:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53280 $"

from zope.interface import implements
from interfaces import IItemsFilter
from itemsfilterrecord import ItemsFilterRecord

class ItemsFilter(object) :
    implements(IItemsFilter)
    def __init__(self,context) :
        self.context = context

    
    def __getitem__(self,name) :
        return ItemsFilterRecord(self.context,name)
                        
                                       
        
