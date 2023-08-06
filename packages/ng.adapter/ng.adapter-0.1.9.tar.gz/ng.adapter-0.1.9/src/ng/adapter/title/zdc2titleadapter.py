### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The adapter Contained2TitleAdapter that adopt IAttributeAnnotatable
   interface to ITitle interface

$Id: product.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.component import adapts
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.dublincore.interfaces import IZopeDublinCore
from contained2titleadapter import Contained2TitleAdapter

class ZDC2TitleAdapter(Contained2TitleAdapter) :

    adapts(IAttributeAnnotatable)
    
    @property
    def title(self) :
        title = IZopeDublinCore(self.context).title
        if not title :
            try:
                return super(ZDC2TitleAdapter, self).title
            except TypeError:
                return title
        
        return title
