### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: breadcrumb.py 13315 2007-11-27 16:11:50Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 13315 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.component import adapts
from breadcrumbbase import BreadCrumbBase
from interfaces import IBreadCrumb

class Stop2BreadCrumbAdapter(BreadCrumbBase) :
    
    def path(self, iface=IBreadCrumb):
        return []
