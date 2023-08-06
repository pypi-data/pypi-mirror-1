===========
stxnext.pdb
===========

Overview
========

This is standard `Python Debugger`_ extended with few features that makes
debugging easier.

stxnext.pdb offer convenience mainly for zope users, but can be used for 
other python projects too.


Features
========

New features added to standard pdb:

* improved *dir* function. Standard *dir* function lists names of all
  methods and attributs of some object. This improved *dir* prints 
  output from this function in few columns. Also possible is filtering
  using regular expressions.
   
  Examples::
  
    (STX Next pdb) obj = object()
    (STX Next pdb) dir(obj)
    __class__                                 __reduce__ 
    __delattr__                               __reduce_ex__ 
    __doc__                                   __repr__ 
    __getattribute__                          __setattr__ 
    __hash__                                  __str__ 
    __init__                                   
    __new__ 
    (STX Next pdb) dir obj attr
    __delattr__                               __setattr__ 
    __getattribute__                           
    (STX Next pdb) dir obj ^__[r-z]+
    __reduce__                                __setattr__ 
    __reduce_ex__                             __str__ 
    __repr__                                   
                                             
* *info* command prints basic information about object.
 
  Examples::
  
    (STX Next pdb) info obj
    type:        <type 'object'>
    class:       <type 'object'>
    id:          140460386956752
    str:         <object object at 0x7fbf7b7835d0>
    repr:        <object object at 0x7fbf7b7835d0>
    docstring:   The most base type

* *update_locals* (*ul*) - update current locals by few useful variables
  and functions. If stxnext.pdb can find zope or plone it imports frequently
  used functions (e.g. getToolByName, getMultiAdapter, alsoProvides). If 
  *context* is available it can also import plone tools. stxnext.pdb looks
  for variables named *self.context*, *context* and *self* in current locals.
  If context should be other it can be passwd as parameter:
  
  Examples::
     
    (STX Next pdb) update_locals #zope found, context unknown
    New locals:
        Attribute
        Interface
        ...
        schema
        sys
        
    (STX Next pdb) ul this_is_context #zope and plone found, correct context
    New locals:
        Attribute
        Interface
        ...
        sys
        uid_catalog
    
     
Using
=====

stxnext.pdb can be opened by standard pdb invoke - only pdb must be imported
from stxnext module::
 
  >>> import pdb;pdb.set_trace() #open standard pdb
  (Pdb) c
  >>> from stxnext import pdb;pdb.set_trace() #
  (STX Next pdb) c
  
If zope instance runned with ``debug-mode=on`` pdb can be invoked from web
browser - just add *pdb* to url (e.g. http://127.0.0.1:8080/plonesite/pdb).
In this approach stxnext.pdb tries to turn on *tab completion* - see `rlcompleter 
documentation`_.


Installation
============

Alternatively, if you are using zc.buildout to manage your project, 
you can do this:

* Add ``stxnext.pdb`` to the list of eggs to install, e.g.::

    [buildout]
    ...
    eggs =
        ...
        stxnext.pdb
        
* If you're using plone.recipe.zope2instance recipe to manage your 
  instance add this lines to install a ZCML slug::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        ...
        stxnext.pdb
      
* If you're using zc.zope3recipes:application recipe to manage your 
  instance add this lines to install a ZCML slug::

    [instance]
    recipe = zc.zope3recipes:application
    ...
    site.zcml =
        ...
        <include package="stxnext.pdb" />       
      
* Re-run buildout, e.g. with::

    $ ./bin/buildout
        
You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.


References
==========

* `stxnext.pdb home page`_
* `stxnext.pdb at pypi`_
* `Python Debugger`_
* `rlcompleter documentation`_

.. _stxnext.pdb home page: http://stxnext.pl/open-source/stxnext.pdb
.. _stxnext.pdb at pypi: http://pypi.python.org/pypi/stxnext.pdb/
.. _Python Debugger: http://docs.python.org/lib/module-pdb.html
.. _rlcompleter documentation: http://docs.python.org/lib/module-rlcompleter.html


Author & Contact
================

:Author: Wojciech Lichota <``wojciech.lichota[at]stxnext.pl``>

.. image:: http://stxnext.pl/open-source/files/stx-next-logo

**STX Next** Sp. z o.o.

http://stxnext.pl

info@stxnext.pl
