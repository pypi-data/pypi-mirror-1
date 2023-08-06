# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: checktocontain.py 51874 2008-10-20 17:22:49Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"

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
        
        
