### -*- coding: utf-8 -*- #############################################
#######################################################################
"""NULL ISublocations adapter may be use to deny event distribution
into object subtree 

$Id: nullsublocations.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import Interface, implements
from zope.location.interfaces import ISublocations

class NullSublocations(object):
    """Get the null sublocations for a object """
    implements(ISublocations)

    def __init__(self, context):
        self.context = context

    def sublocations(self):
        if False :
            yield None
