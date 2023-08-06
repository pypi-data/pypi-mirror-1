# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: checktocontain.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Dima Khozin & Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"
__date__ = "$Date: 2008-09-23 23:47:45 +0400 (Втр, 23 Сен 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements, implementedBy
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import SimpleHandler
from zope.security.proxy import removeSecurityProxy
from pd.lib.utility import name2klass
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied

class FalseCheckToContain(SimpleHandler):
    """++checktocontain++ -> False"""
    implements(ITraversable)
    def traverse(self,name,ignored) :
        """ Всегда возвращаем "ложно" для не-контейнеров  """
        return False 


class CheckToContain(FalseCheckToContain):
    """ ++checktocontain++"""

    def traverse(self,name,ignored) :
        """ Return True in name class can be contained in context """
        print 1
        klass = name2klass(name)
        print 2
        parent = implementedBy(klass).get('__parent__')
        print 3
        if parent is not None :
            print 4
            try :
                print 5
                parent.validate(self.context)        
                print 6
            except ConstraintNotSatisfied :
                print 7
                return False 
        print 8                
        return True
        
        
