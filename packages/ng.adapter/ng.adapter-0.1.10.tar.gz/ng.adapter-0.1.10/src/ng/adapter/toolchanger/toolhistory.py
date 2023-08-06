### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ToolHistory class for the Zope 3 based package,
class used to save navigation history in request annotations.

$Id: toolhistory.py 51874 2008-10-20 17:22:49Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"

from zope.interface import implements,implementedBy
from interfaces import IToolHistory

class ToolHistory(object) :
    __doc__ = __doc__
    implements(IToolHistory)

    best = u""
    up = u""
          
          
