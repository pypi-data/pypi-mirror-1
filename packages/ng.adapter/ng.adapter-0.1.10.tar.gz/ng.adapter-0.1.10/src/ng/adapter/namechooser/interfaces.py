### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 51874 2008-10-20 17:22:49Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51874 $"
 
from zope.interface import Interface

class INameChooserAble(Interface) :
    """ Interface which allow to use INameChooser """
                    
