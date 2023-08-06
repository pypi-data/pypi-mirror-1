### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adaptive URL view components

$Id: toolurl.py 51810 2008-10-02 15:19:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51810 $"

from zope.interface import Interface,implements,implementedBy
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from interfaces import IToolURL, IToolHistory
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL

def toolURL(ob, request):
    return getMultiAdapter((ob, request), name="tool_url")()

class ToolURL(BrowserView):
    implements(IToolURL)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        url = str(adaptiveURL(self.context,self.request))
        method = IToolHistory(self.request).best
        if not method :
            method = str(self.request.URL)[len(self.request.URL[-1])+1:]
        url += '/++tool++' + method 
        try :
            getMultiAdapter([self.context,self.request],Interface,context=self.context,name=method[2:])
        except Exception,msg :
            method = u''
        return url + '/' +  method

    def __call__(self) :
        return self.__str__()


