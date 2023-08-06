### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based AdaptiveURL  package

$Id: interfaces.py 52382 2009-01-19 13:26:41Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52382 $"
 
from zope.interface import Interface

from zope.schema import URI
                
class ICheckSublocation(Interface):

    def check(ob) :
        """ Return true if ob is sublocation of context """
        
        
