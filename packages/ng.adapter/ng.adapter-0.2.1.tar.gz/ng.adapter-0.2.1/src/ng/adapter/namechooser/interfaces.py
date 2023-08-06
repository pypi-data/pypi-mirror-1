### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 53381 2009-07-05 22:27:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 53381 $"
 
from zope.interface import Interface

class INameChooserAble(Interface) :
    """ Interface which allow to use INameChooser """
                    
class INameChooserSafeAble(Interface) :
    """ Interface which allow to use INameChooserSafe """

class INameChooserSafeWithoutSpaceAble(Interface) :
    """ Interface which allow to use INameChooserSafe """

                    
