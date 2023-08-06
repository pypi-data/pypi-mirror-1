### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based AdaptiveURL  package

$Id: interfaces.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 51772 $"
 
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
        