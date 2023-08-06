### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.requestcache package

$Id: interfaces.py 51874 2008-10-20 17:22:49Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"

from zope.interface import Interface

class IRequestCache(Interface):

    def cache(period=600):
        """ Set response header to cache period second """

    def nocache() :
        """ Set response header to nocache """
