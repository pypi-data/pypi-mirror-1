### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter to IRecordSize interface which provide object record size in database

$Id: recordsize.py 51772 2008-09-23 19:47:45Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 51772 $"

from interfaces import IRecordSize 
import cPickle
import tempfile
from zope.location.interfaces import ILocation

class ReferenceCut(object) :

    def __init__(self, location):
        self.location = location
        self.pids_by_id = {}
        self.others_by_pid = {}
        self.load = self.others_by_pid.get

    def id(self, ob):
        if ILocation.providedBy(ob):
            if self.location is not ob :
                if id(ob) in self.pids_by_id:
                    return self.pids_by_id[id(ob)]
                pid = len(self.others_by_pid)
                pid += 1

                self.pids_by_id[id(ob)] = pid
                self.others_by_pid[pid] = ob
                return pid
                
        return None

class RecordSizeAdapter(object) :
    def __init__(self,context) :
        self.context = context

    @property        
    def size(self) :
      tmp = tempfile.TemporaryFile()
      persistent = ReferenceCut(self.context)

      # Pickle the object to a temporary file
      pickler = cPickle.Pickler(tmp, 2)
      pickler.persistent_id = persistent.id
      pickler.dump(self.context)

      # Now load it back
      return tmp.tell()
