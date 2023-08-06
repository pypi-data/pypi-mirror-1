argvalidate - Python argument validator library documentation
===========================================================================

Contents:

.. toctree::
   :maxdepth: 2

   argvalidate
   envvars

Primer
======

argvalidate is a small Python module which gives developers the opportunity
to do both argument- and return-value type checking.
This basically enables you to be sure that an argument passed to a function and
the return value of a function is of a specific type, or even one of a list 
specified types.

argvalidate provides you with three different decorators, which define the
rules for argument types and return value types: 

:func:`~argvalidate.func_args`, 
:func:`~argvalidate.method_args` and
:func:`~argvalidate.return_value`.

argvalidate either raises an :ref:`exception <argvalidate-exceptions>` or
creates a Python warning if it detects an error. This behaviour can be
configured via :ref:`environment variables <argvalidate-envvars>`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

