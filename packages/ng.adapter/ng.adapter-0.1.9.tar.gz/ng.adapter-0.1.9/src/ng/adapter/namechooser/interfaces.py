### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"
 
from zope.interface import Interface

class INameChooserAble(Interface) :
    """ Interface which allow to use INameChooser """
                    
