Short description of ng.adapter
===============================

This package has developed as the library of small adapters for the
different dark purposes.

Adapter mtime
-------------

Adapter mtime intdends for getting object modification time. Object
modification time determine on the IPersistent level and this is an exactly
in the most cases, but sometimes we need some of hooks to know object
modification time and adapter mtime helps us in this.

Adapter mtime adapts IPersistent interface to IMTime interface. IMTime interface
has the following fields:
    
    mtime
       time of the last modification of object
