### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.app.container.interfaces import IContained
from zope.component import adapts
from titleadapterbase import TitleAdapterBase

class Contained2TitleAdapter(TitleAdapterBase) :

    adapts(IContained)
    
    @property
    def title(self) :
        return IContained(self.context).__name__
