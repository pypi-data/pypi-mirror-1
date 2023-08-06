### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Check to sublocation

$Id: checksublocation.py 52382 2009-01-19 13:26:41Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52382 $"

from zope.interface import implements,implementedBy
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from interfaces import ICheckSublocation

from zope.proxy import sameProxiedObjects
from zope.location.interfaces import ILocation

class SiteCheckSublocation(BrowserView):
    implements(ICheckSublocation)

    def check(self,ob):
        return sameProxiedObjects(self.context, ob)

class CheckSublocation(SiteCheckSublocation):

    def check(self, ob) :
        if super(CheckSublocation,self).check(ob) :
            return True

        container = ILocation(self.context).__parent__
        return getMultiAdapter((container, self.request),name='checksublocation').check(ob)
