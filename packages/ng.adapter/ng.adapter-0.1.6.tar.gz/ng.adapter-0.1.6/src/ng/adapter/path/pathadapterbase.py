### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.interface import implements
from interfaces import IPath

class PathAdapterBase(object) :

    implements(IPath)
    
    def __init__(self, context) :
        self.context = context

    @property
    def tailpath(self) :
       return self._tailpath((self.name,))
       
       