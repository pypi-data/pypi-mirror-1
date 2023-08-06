### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Object size interface

$Id: interfaces.py 51772 2008-09-23 19:47:45Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from zope.interface import Interface
from zope.schema import Int, Field

class IRecordSize(Interface):
    """Record Size interface"""

    size = Int(
        title=u"Size",
        description=u"Size of database record",
        default=0,
        required=True)


