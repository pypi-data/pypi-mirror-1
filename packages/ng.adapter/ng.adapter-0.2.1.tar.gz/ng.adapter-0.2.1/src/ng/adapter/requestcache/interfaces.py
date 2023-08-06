### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
Interfaces for the Zope 3 based ng.adapter.requestcache package

$Id: interfaces.py 51794 2008-09-26 07:48:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51794 $"

from zope.interface import Interface

class IRequestCache(Interface):

    def cache(period=600):
        """ Set response header to cache period second """

    def nocache() :
        """ Set response header to nocache """
