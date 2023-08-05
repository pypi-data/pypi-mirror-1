### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 49480 2008-01-15 18:17:04Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49480 $"
 
from zope.interface import Interface

class INameChooserAble(Interface) :
    """ Interface which allow to use INameChooser """
                    
