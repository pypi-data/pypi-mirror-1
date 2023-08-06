.. _argvalidate-module:

argvalidate Module
==================

.. automodule:: argvalidate

Below you can find the documentation of the public API of argvalidate.

Even though more constants, decorators, exceptions and functions may be
specified in the argvalidate module, only those described here form the API 
and are intended for public use.

.. note::

   Do *not* rely on any internals of argvalidate, as these may change at any 
   time, without further notice.

Decorators
----------

.. autofunction:: func_args
.. autofunction:: method_args
.. autofunction:: return_value

Helpers
-------

.. autofunction:: one_of
.. autofunction:: raises_exceptions
.. autofunction:: warns_kwarg_as_arg


.. _argvalidate-exceptions:

Exceptions
----------
.. exception:: ArgvalidateException

   This exception is set at run time and is either an 
   :exc:`ArgvalidateErrorException` or an 
   :exc:`ArgvalidateErrorWarning`.
   
   This exception can be used to catch *all* exceptions argvalidate may raise.
   

.. autoexception:: ArgvalidateErrorException
.. autoexception:: ArgvalidateErrorWarning
.. autoexception:: ArgumentTypeException
.. autoexception:: ReturnValueTypeException
.. autoexception:: ArgumentLengthException
.. autoexception:: DecoratorLengthException
.. autoexception:: DecoratorNonKeyLengthException
.. autoexception:: DecoratorKeyUnspecifiedException
