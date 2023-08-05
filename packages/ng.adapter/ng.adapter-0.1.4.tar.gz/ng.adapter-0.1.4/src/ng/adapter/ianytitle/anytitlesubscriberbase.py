### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The base adapter 

$Id: anytitilesubscriberbase.py 12897 2007-11-10 15:32:08Z cray $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 12897 $"

class AnyTitileSubscriberBase(object) :

    order = 0

    def __init__(self,context) :
        self.context = context

    def __cmp__(self,x) :
        return cmp(self.order,x.order)