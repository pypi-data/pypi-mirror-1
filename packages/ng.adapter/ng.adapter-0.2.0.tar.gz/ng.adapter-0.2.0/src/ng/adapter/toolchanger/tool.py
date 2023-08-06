# -*- coding: utf-8 -*-
"""The Tool class.

$Id: tool.py 51810 2008-10-02 15:19:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51810 $"

from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import SimpleHandler
from interfaces import IToolHistory
from zope.location import location
from zope.security.proxy import removeSecurityProxy

class Tool(SimpleHandler):
    """ ++tool++"""

    implements(ITraversable)

    def __init__(self,context,request) :
        self.request = request
        super(Tool,self).__init__(context,request)

    def traverse(self,name,ignored) :
        """Сохранение вида по умолчанию"""
        IToolHistory(self.request).best = name

        return self.context
        res = location.LocationProxy(
              removeSecurityProxy(self.context), self.context, '++tool++'+name
              )

        return res


        
