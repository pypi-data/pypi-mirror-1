### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Object size interface

$Id: interfaces.py 49627 2008-01-21 15:31:34Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49627 $"

from zope.interface import Interface
from zope.schema import Int, Field

class IRecordSize(Interface):
    """Record Size interface"""

    size = Int(
        title=u"Size",
        description=u"Size of database record",
        default=0,
        required=True)


