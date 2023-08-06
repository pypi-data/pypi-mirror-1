# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: nsinterface.py 1074 2007-01-19 03:50:47Z cray $
"""
__author__  = "Dima Khozin & Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 1074 $"
__date__ = "$Date: 2007-01-19 06:50:47 +0300 (Птн, 19 Янв 2007) $"
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
        
