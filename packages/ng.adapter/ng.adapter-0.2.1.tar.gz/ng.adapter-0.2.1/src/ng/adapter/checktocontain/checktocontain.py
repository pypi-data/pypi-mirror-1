# -*- coding: utf-8 -*-
"""The nsinterface class.

$Id: checktocontain.py 52247 2008-12-29 16:54:17Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52247 $"

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
        klass = name2klass(name)
        parent = implementedBy(klass).get('__parent__')
        if parent is not None :
            try :
                parent.validate(self.context)        
            except ConstraintNotSatisfied :
                return False 
            except :
                return True
        return True
        
        
