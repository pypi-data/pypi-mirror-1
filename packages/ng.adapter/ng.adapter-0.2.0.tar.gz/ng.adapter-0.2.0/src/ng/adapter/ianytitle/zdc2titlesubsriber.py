### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The adapter ZDC2TitleSubscribe that adopt IAttributeAnnotatable
   interface to ITitle interface

$Id: zdc2titlesubscribe.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__credits__  = "Yegor Shershnev"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

from zope.component import adapts
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.dublincore.interfaces import IZopeDublinCore
from anytitlesubscriberbase import AnyTitleSubscriberBase


class ZDC2TitleSubscribe( AnyTitleSubscriberBase ) :
    order = 1
    adapts(IAttributeAnnotatable)
    
    @property
    def title(self) :
        return IZopeDublinCore(self.context).title


