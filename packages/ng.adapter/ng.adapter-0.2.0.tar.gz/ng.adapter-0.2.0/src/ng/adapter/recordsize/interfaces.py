### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Object size interface

$Id: interfaces.py 50085 2008-01-15 07:20:15Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50085 $"

from zope.interface import Interface
from zope.schema import Int, Field

class IRecordSize(Interface):
    """Record Size interface"""

    size = Int(
        title=u"Size",
        description=u"Size of database record",
        default=0,
        required=True)


