### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Class used to access to objects sequence filtered by named condition

$Id: itemsfilterrecord.py 53280 2009-06-14 11:15:58Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 53280 $"

from zope.interface import implements
from zope.app.container.interfaces import IReadContainer
from zope.component import getMultiAdapter, getAdapter, ComponentLookupError
from interfaces import IItemsFilterCondition

class ItemsFilterRecord(object) :
    """Sequence of objects filtered by condition registered as "name" """
    implements(IReadContainer)
    
    def __init__(self,context,name) :
        self.context = context
        self.name = name


    def keys(self) :
        return [ x for x,y in self.items() ]
        
    def values(self) :
        return [ y for x,y in self.items() ]
                                       
    def items(self) :
        for key in self.context.keys() :
            try :
                yield (key,self[key])
            except KeyError :
                pass                
    
    def __getitem__(self,name) :
        value = self.context[name]
        try :
            if not getAdapter(value,IItemsFilterCondition,name=self.name)() :
                raise KeyError,name                
        except ComponentLookupError :
            raise KeyError
        return value            
        