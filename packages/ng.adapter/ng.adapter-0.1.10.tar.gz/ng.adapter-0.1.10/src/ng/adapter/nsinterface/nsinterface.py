# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: nsinterface.py 51874 2008-10-20 17:22:49Z cray $
"""
__author__  = "Dima Khozin & Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"
__date__ = "$Date: 2008-10-20 21:22:49 +0400 (Пнд, 20 Окт 2008) $"
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
        
