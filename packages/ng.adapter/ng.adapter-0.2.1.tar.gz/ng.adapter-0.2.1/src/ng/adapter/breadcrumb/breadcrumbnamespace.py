### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: breadcrumb.py 13315 2007-11-27 16:11:50Z cray $
"""
__author__  = "Uzorin, 2008"
__license__ = "GPL"
__version__ = "$Revision: 13315 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.traversing.interfaces import ITraversable
from interfaces import IBreadCrumb
from pd.lib.utility import name2klass
                
class BreadCrumbNamespace(object):
    implements(ITraversable)
    
    def __init__(self, context, request) :
        self.context = context
        self.request = request                   

    def traverse(self,name,ignored) :
        bc = IBreadCrumb(self.context,None)
        if bc is None:
            return []
        if name is None or len(name) == 0:
           name = "ng.adapter.breadcrumb.interfaces.IBreadCrumb"
        iface = name2klass(name)
        return bc.path(iface)
