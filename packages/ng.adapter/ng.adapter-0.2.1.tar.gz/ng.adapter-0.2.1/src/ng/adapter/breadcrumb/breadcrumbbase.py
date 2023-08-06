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
from interfaces import IBreadCrumb
                
class BreadCrumbBase(object) :
    implements (IBreadCrumb)

    def __init__(self, ob) :
        self.context = ob
