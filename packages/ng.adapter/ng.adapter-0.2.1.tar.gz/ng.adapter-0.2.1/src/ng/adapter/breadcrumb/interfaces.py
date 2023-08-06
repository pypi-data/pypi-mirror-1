### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 50375 2008-01-27 22:29:28Z pitch $
"""
__author__  = "Uzorin, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50375 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
class IBreadCrumbList(Interface):
    pass

class IBreadCrumb(Interface):
 

    title = TextLine( title=u"Название объекта",
                      description=u"Название объекта",
                      default=u"",
                      required=True)

    def url(self,request):
        pass

    def path(self, iface):
        pass

class IBreadCrumbStop(Interface):
    pass
