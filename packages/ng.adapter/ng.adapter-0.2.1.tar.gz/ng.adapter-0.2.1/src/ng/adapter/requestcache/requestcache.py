### -*- coding: utf-8 -*- #############################################
#######################################################################
""" IRequest Adapter to IRequestCache interface

$Id: requestcache.py 51794 2008-09-26 07:48:12Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51794 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
import time
from interfaces import IRequestCache
from ng.app.registry.interfaces import IRegistry

class RequestCache(object) :
    implements(IRequestCache)

    def __init__(self, request):
        super(RequestCache, self).__init__(request)
        self.request = request

    def cache(self,period=600) :
        self.request.response.setHeader('Expires',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()+period))
            )
        self.request.response.setHeader('Last-Modified',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()-period))
            )
                  
    def nocache(self) :
        self.request.response.setHeader('Pragma', 'no-cache')
        self.request.response.setHeader('Cache-Control', 'no-cache')    

        self.request.response.setHeader('Expires',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()))
            )

        self.request.response.setHeader('Last-Modified',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()))
            )

class RequestCacheView(RequestCache) :
    implements(IRequestCache)

    cache_use = True
    cache_period = 600
    cache_use_as_nocache = False

    def __init__(self, context, request):
        self.context = context
        self.request = request
        try :
            IRegistry(self).export(self,'cache_use','cache_period', 'cache_use_as_nocache')
        except TypeError :
            pass

    def cache(self, period=None) :
        if period is None :
            period = self.cache_period
        if self.cache_use :            
            if self.cache_use_as_nocache :
                self.nocache()
            else :
                super(RequestCacheView).cache(period)
                