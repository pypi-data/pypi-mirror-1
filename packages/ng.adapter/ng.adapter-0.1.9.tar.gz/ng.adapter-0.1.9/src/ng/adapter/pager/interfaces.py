### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.pager package

$Id: interfaces.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import Interface
from zope.schema import Field, Tuple, Int, Bool

class IPager(Interface):

    def setPagerParameters(revert=None, orphan=None,size=None) :
        """ Set Pager Parameters """
        
    def getOb(key) :
        pass
        
    def getKey(index) :
        pass

    have_before = Bool()

    befores = Tuple()

    beforeURLs = Tuple()

    before  = Field()

    beforeURL = Field()

    chunk   = Tuple()

    keys    = Tuple()

    index   = Int()

    after   = Field()

    afterURL = Field()

    afters  = Tuple()        

    afterURLs  = Tuple()        

    have_after = Bool()

    len     = Int()

class IPagerSource(Interface) :
    def __getitem__(key) :
        """ Return object by key """
        
    def keys() :        
        """ Return ordered key sequence """
        