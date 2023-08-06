### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adaptive URL view components

$Id: adaptiveurl.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from interfaces import IAdaptiveURL, IAdaptiveURLRoot
from zope.traversing.browser.absoluteurl import _safe, _insufficientContext
from zope.proxy import sameProxiedObjects
import urllib

class DoAdapt(Exception) :
    """ Adaptation need """

def adaptiveURL(ob, request):
    return getMultiAdapter((ob, request), name="adaptive_url")()

class SiteAdaptiveURL(BrowserView):
    implements(IAdaptiveURL)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        request = self.request

        if sameProxiedObjects(context, request.getVirtualHostRoot()):
            return request.getApplicationURL()
        elif request.getVirtualHostRoot() :
            raise DoAdapt

        url = request.getApplicationURL()
 
        try :
            url =+  self._getContextName(context) 
        except TypeError :
            pass
 
        return url                        


    def __call__(self) :
        return self.__str__()

    def _getContextName(self, context):
        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError(_insufficientContext)
        return '/' + urllib.quote(name.encode('utf-8'), _safe)        

class AdaptiveURL(SiteAdaptiveURL):

    def __str__(self):
        context = self.context
        request = self.request

        # The application URL contains all the namespaces that are at the
        # beginning of the URL, such as skins, virtual host specifications and
        # so on.
        if (context is None
            or sameProxiedObjects(context, request.getVirtualHostRoot())):
            return request.getApplicationURL()
        
        try :            
            urlroot=IAdaptiveURLRoot(context)
        except TypeError :
            url = self._up(context,request)
        else :
            try :
                url = self._up(context,request)                
            except DoAdapt :
                return urlroot.adaptive_url
            
        url += self._getContextName(context)
        return url

                                
    def _up(self, context, request) :
        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(_insufficientContext)

        return str(getMultiAdapter((container, request),name='adaptive_url'))
