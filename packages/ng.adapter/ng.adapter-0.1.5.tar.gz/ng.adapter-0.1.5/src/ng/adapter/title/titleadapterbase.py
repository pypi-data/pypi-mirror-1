### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from interfaces import ITitle
from zope.interface import implements

class TitleAdapterBase(object) :

    implements(ITitle)
    
    def __init__(self, context) :
        self.context = context
