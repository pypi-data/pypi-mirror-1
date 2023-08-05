dm.zdoc
=======

Tiny wrapper around ``pydoc`` to make it usable for Zope.

A wrapper is necessary because Zope makes use of Python packages' ``__path__``
feature and this is not well supported by ``pydoc``.

Zope' environment variables ``INSTANCE_HOME`` and ``SOFTWARE_HOME`` must be 
set before the module can be imported.

Usage
=====

``zdoc`` can either be used via the script ``dmzdoc`` or via module import.
Note, that in both cases the Zope environment variables ``INSTANCE_HOME``
and ``SOFTWARE_HOME`` must be defined. They tell ``zdoc`` where the Zope sources
can be found.

Use via ``dmzdoc``
------------------

The script ``dmzdoc`` is installed when you have ``setuptools`` installed.

Otherwise, you must install it yourself. It has the following content::

   import dm.zdoc; dm.zdoc.cli()

``dmzdoc`` has the exact same options and parameters as ``pydoc``,
documented in pydoc_.

Use via module import
---------------------

The module ``dm.zdoc`` defines exactly the same objects as ``pydoc``.
Unfortunately, ``pydoc`` has no module level documentation - but you
can use ``pydoc`` to get a source documentation.

.. _pydoc: http://docs.python.org/lib/module-pydoc.html
