### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Zope.app.catalog.ResultSet Adapter to IPagerSource Interface

$Id: resultset2pagersourceadapter.py 50637 2008-02-12 21:29:19Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50637 $"

from zope.interface import implements,Interface
from zope.component import adapts
from interfaces import IPagerSource

class List(list) :
    def __getitem__(self,index) :
        return super(List,self).__getitem__(int(index))

    def index(self,index) :
        return super(List,self).index(int(index))

class ResultSet2PagerSourceAdapter(object):
    __doc__ = __doc__

    implements(IPagerSource)

    def __init__(self, context):
        self.context = context
       
    def keys(self) :
        return List(self.context.uids)
        
    def __getitem__(self,key) :
        return self.context.uidutil.getObject(key)
    
