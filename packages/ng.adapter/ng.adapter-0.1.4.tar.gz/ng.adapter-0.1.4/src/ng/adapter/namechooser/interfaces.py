### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 49627 2008-01-21 15:31:34Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49627 $"
 
from zope.interface import Interface

class INameChooserAble(Interface) :
    """ Interface which allow to use INameChooser """
                    
