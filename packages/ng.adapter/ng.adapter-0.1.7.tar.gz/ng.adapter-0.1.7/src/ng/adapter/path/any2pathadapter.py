### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Any2PathAdapter class for the Zope 3 based ng.adapter.path package

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.interface import Interface
from zope.component import adapts
from pathadapterbase import PathAdapterBase

class Any2PathAdapter(PathAdapterBase) :

    adapts(Interface)
    
    path = ""

    titledpath = ""

    tailpath = ()

    name = ""
    
    def _tailpath(self,path) :
        return path
