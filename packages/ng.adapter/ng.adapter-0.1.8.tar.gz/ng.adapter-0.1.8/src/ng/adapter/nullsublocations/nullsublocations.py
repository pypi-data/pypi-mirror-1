### -*- coding: utf-8 -*- #############################################
#######################################################################
"""NULL ISublocations adapter may be use to deny event distribution
into object subtree 

$Id: nullsublocations.py 50795 2008-02-21 10:58:27Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50795 $"

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
