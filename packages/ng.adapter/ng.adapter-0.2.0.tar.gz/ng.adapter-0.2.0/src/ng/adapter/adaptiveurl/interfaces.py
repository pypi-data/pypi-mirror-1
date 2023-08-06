### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based AdaptiveURL  package

$Id: interfaces.py 51805 2008-10-02 10:37:17Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51805 $"
 
from zope.interface import Interface

from zope.schema import URI
                
class IAdaptiveURL(Interface):

    def __unicode__():
        """Returns the URL as a unicode string."""

    def __str__():
        """Returns an ASCII string with all unicode characters url quoted."""

    def __repr__():
        """Get a string representation """

    def __call__():
        """Returns an ASCII string with all unicode characters url quoted."""

class IAdaptiveURLRoot(Interface) :
    
    adaptive_url = URI( title = u"Site Root URL" )
        