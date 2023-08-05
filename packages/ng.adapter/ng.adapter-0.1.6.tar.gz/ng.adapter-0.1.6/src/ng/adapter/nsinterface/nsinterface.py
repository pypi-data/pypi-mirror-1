# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: nsinterface.py 49951 2008-02-06 20:16:04Z cray $
"""
__author__  = "Dima Khozin & Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49951 $"
__date__ = "$Date: 2008-02-06 23:16:04 +0300 (Срд, 06 Фев 2008) $"
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
        
