### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Any Interface Adapter to IPager Interface

$Id: pageradapter.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import implements,Interface
from zope.component import adapts
from ng.app.registry.interfaces import IRegistry
from zope.app.zapi import getUtility
from zope.cachedescriptors.property import CachedProperty
from interfaces import IPager, IPagerSource
from zope.publisher.interfaces.http import IHTTPRequest
from ng.adapter.requestext.interfaces import IRequestExt
from zope.traversing.browser import absoluteURL

class PagerAdapter(object):
    __doc__ = __doc__

    implements(IPager)
    adapts(Interface,IHTTPRequest)
    
    orphan = 3
    size = 10
    revert = False
    _absolute_url = None

    def __init__(self, context, request):
        self.context = IPagerSource(context)
        self.request = request
        self.requestext = IRequestExt(request)
        self.requestext.setParameters(exclude=('current',))

    def setPagerParameters(self,revert=None,orphan=None,size=None,context=None) :
        if context :
            self._absolute_url = absoluteURL(context,self.request)
        if revert :
            self.revert = revert 
        if orphan :
            self.orphan = orphan 
        if size :
            self.size = size 
        try :            
            IRegistry(self.context).export(self,'orphan','size','revert')
        except TypeError :
            pass

    def getOb(self,key) :
        return self.context[key]
        
    def getKey(self,index) :
        return self.keys[index]

    @CachedProperty
    def absolute_url(self) :
        return str(self.request.URL)
    
        if self._absolute_url :
            return self._absolute_url
        else :
            absoluteURL(self.context,self.request)                    


    @CachedProperty
    def keys(self) :
        res = self.context.keys()
        if self.revert :
            res.reverse()
        return res            
         
    @CachedProperty
    def index(self) :
        try :
            curr = self.request.form['current']
        except KeyError :
            return 0
                    
        return self.keys.index(curr)

    @CachedProperty
    def beforeURLs(self) :
        for item in self.befores :
            yield self.absolute_url+'?'+self.requestext.query(current=item)
            

    @CachedProperty
    def befores(self) :
        for item in xrange(0,self._before,self.size-self.orphan) :
            yield self.getKey(item)
            

    @CachedProperty
    def have_before(self) :
        try :    
            return self._before < self.index
        except Exception,msg :
            print "RRRR",msg            
            
        try :
            self._before
        except IndexError :
            return False
        except Exception,msg:
            print "qq1",msg
        else :
            return True                        

    @CachedProperty
    def beforeURL(self) :
        return self.absolute_url+'?'+self.requestext.query(current=self.before)

    @CachedProperty
    def before(self) :
        return self.getKey(self._before)
        
    @CachedProperty
    def _before(self) :
        return max(self.index + self.orphan - self.size,0)
                
    @CachedProperty
    def chunk(self) :
    
        for item in xrange(self.index,min(self.index+self.size,self.len),1) :
            yield self.getOb(self.getKey(item))
            
    @CachedProperty
    def have_after(self) :
        return self._after < self.len-self.orphan
            
    @CachedProperty
    def afterURL(self) :
        return self.absolute_url+'?'+self.requestext.query(current=self.after)

    @CachedProperty            
    def after(self) :
        return self.getKey(self._after)
        
    @CachedProperty            
    def _after(self) :
        return min(self.index + self.size-self.orphan,self.len-1)

    @CachedProperty
    def afterURLs(self) :
        for item in self.afters :
            yield self.absolute_url+'?'+self.requestext.query(current=item)
            
    @CachedProperty
    def afters(self) :
        for item in xrange(self._after,self.len-1,self.size-self.orphan) :
            yield self.getKey(item)
    
    @CachedProperty
    def len(self) :
        return len(self.keys)

        