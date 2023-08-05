### -*- coding: utf-8 -*- #############################################
#######################################################################
""" OrderedContainer Adapter to IPagerSource Interface

$Id: orderedcontainer2pagersourceadapter.py 49617 2008-01-21 13:24:50Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49617 $"

from zope.interface import implements,Interface
from zope.component import adapts
from interfaces import IPagerSource
from zope.cachedescriptors.property import CachedProperty
from zope.app.container.interfaces import IOrderedContainer

class OrderedContainer2PagerSourceAdapter(object):
    __doc__ = __doc__

    implements(IPagerSource)
    adapts(IOrderedContainer)

    def __init__(self, context):
        self.context = context
       
    def keys(self) :
        return self.context.keys()
        
    def __getitem__(self,key) :
        return self.context[key]               
    
