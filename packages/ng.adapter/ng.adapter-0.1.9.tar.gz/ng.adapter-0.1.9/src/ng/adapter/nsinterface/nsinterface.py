# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: nsinterface.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Dima Khozin & Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"
__date__ = "$Date: 2008-09-23 23:47:45 +0400 (Втр, 23 Сен 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.component.interface import nameToInterface
from zope.traversing.namespace import SimpleHandler
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.location import location

class Nsinterface(SimpleHandler):
    """ ++interface++"""

    implements(ITraversable)

    def traverse(self,name,ignored) :
        """алгоритм приведения контекстного объекта к нужному интерфейсу"""
        res = nameToInterface(self.context,name)(self.context)
        res = removeSecurityProxy(res)
        if True : #not IPhysicallyLocatable(res, False):
            res = location.LocationProxy(
                res, self.context, '++nsinterface++'+name)
            return res
        return res
        
