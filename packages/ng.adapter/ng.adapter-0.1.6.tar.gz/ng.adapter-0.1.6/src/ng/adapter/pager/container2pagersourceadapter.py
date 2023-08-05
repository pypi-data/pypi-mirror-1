### -*- coding: utf-8 -*- #############################################
#######################################################################
""" OrderedContainer Adapter to IPagerSource Interface

$Id: container2pagersourceadapter.py 49951 2008-02-06 20:16:04Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49951 $"

from zope.interface import implements,Interface
from zope.component import adapts
from interfaces import IPagerSource
from zope.cachedescriptors.property import CachedProperty
from zope.app.container.interfaces import IContainer

class Container2PagerSourceAdapter(object):
    __doc__ = __doc__

    implements(IPagerSource)
    adapts(IContainer)

    def __init__(self, context):
        self.context = context
       
    def keys(self) :
        return list(self.context.keys())
        
    def __getitem__(self,key) :
        return self.context[key]               
    
