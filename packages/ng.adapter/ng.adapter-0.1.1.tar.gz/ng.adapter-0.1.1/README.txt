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


Adapter path
------------

Adapter path intdents for getting path from root object to current, Adapter can adopt
any objects to IPath interface. Interface IPath provide followed fields:

    path
        Path from root to current object maked from attribute __name__ of object in between;

    titledpath
        Path from root to current object maked from titles object in between. Titles getting from
        adapter title (ITitle interface);


Adapter title
-------------

Adapter title ntdends for getting object title (for any object).  Adapter can adopt
any objects to ITitle interface. Interface IPath provide followed fields:

    title
        Object title

If current object has not title property, property title of object, adopted
ti IZopeDublinCore return instead, If adopt to IZopeDublinCore is not possible,
property __name__ or class name return instead.

Adapter has been wrote in goot component style and it's posible to write adapter
to ITitle for any specific cases.


Adapter nsinterface
-------------------
   
Adapter nsinterface defince nsinterface namespace to get possibility adopt current
object to any interfacr. Some syntax sample followed::   

    <tal:block define="path context/++nsinterface++ng.adapter.IPath/path">
    
    </tal:block>
    
It usefaul, basicaly, in debugging purpose.

Adapter namechooser
-------------------

If this adapter will be actvated to some container, object, created in this
container will be accept __name__ from ITitle adapter.

To activate adappter, set interface ng.adapter.interfaces.INameChooserAble
on container.
