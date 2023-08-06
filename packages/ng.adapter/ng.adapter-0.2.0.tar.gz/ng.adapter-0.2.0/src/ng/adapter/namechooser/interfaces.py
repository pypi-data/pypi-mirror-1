### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based <> package

$Id: interfaces.py 13229 2007-11-01 19:49:31Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 13229 $"
 
from zope.interface import Interface

class INameChooserAble(Interface) :
    """ Interface which allow to use INameChooser """
                    
