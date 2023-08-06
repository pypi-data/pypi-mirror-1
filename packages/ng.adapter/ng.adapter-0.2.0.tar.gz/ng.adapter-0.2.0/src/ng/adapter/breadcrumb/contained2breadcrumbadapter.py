### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: breadcrumb.py 13315 2007-11-27 16:11:50Z cray $
"""
__author__  = "Uzorin, 2007"
__license__ = "GPL"
__version__ = "$Revision: 13315 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from breadcrumbbase import BreadCrumbBase                
from interfaces import IBreadCrumb
from ng.adapter.ianytitle.interfaces import IAnyTitle
from zope.app.container.interfaces import IContained
from zope.traversing.browser.absoluteurl import absoluteURL

class Contained2BreadCrumbAdapter(BreadCrumbBase) :

    @property
    def title(self):
        try:
            iat = IAnyTitle(self.context)
        except TypeError:
            return self.context.__name__
        return iat.title

    def url(self, request):
        return absoluteURL(self.context, request)

    def path(self, iface=IBreadCrumb):
        ifo = iface(self.context, None)
        sc = IContained(self.context)
        parent = sc.__parent__
        if parent is not None:
            parent = IBreadCrumb(parent, None)

# The four case possible continue

        if parent is None and ifo is None:
            return []
        if parent is None and ifo is not None:
            return [ifo]
        if parent is not None and ifo is None:
            return parent.path(iface)
        if parent is not None and ifo is not None:
            return [ifo] + parent.path(iface)
