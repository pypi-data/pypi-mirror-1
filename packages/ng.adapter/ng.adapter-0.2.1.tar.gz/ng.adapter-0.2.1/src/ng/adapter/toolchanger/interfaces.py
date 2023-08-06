### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based AdaptiveURL  package

$Id: interfaces.py 51810 2008-10-02 15:19:16Z cray $
"""
__author__  = "Andreey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51810 $"
 
from zope.interface import Interface

from zope.schema import TextLine
                
class IToolURL(Interface):

    def __unicode__():
        """Returns the URL as a unicode string."""

    def __str__():
        """Returns an ASCII string with all unicode characters url quoted."""

    def __repr__():
        """Get a string representation """

    def __call__():
        """Returns an ASCII string with all unicode characters url quoted."""


class IToolHistory(Interface) :
    
    best = TextLine(title=u"Best Method", default=u"")
    
    up = TextLine(title=u"Up Best Method", default=u"")

toolhistorykey=u'ng.adapter.tool.toolhistory.ToolHistory'          