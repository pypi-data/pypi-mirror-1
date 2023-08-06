### -*- coding: utf-8 -*- #############5~################################
#######################################################################
"""Adapter to IToolHistory interfaces based on annotations.

$Id: toolhistoryannotationadapter.py 51810 2008-10-02 15:19:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51810 $"

from toolhistory import ToolHistory
from zope.annotation.interfaces import IAnnotations 
from interfaces import toolhistorykey

def ToolHistoryAnnotationAdapter(context) :

    try :
        an = IAnnotations(context)[toolhistorykey]
    except KeyError :
        an = IAnnotations(context)[toolhistorykey] = ToolHistory()
    return an
