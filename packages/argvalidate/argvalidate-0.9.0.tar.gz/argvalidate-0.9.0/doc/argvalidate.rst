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

   The API described here forms the public interface to argvalidate and as such
   will have functionality pending for removal deprecated first.

Decorators
----------

.. autofunction:: accepts
.. autofunction:: returns

.. note::

    Stacking of decorator of the same type (ie. :func:`accepts`
    and :func:`accepts`, :func:`returns` and :func:`returns`) is not possible
    and will cause a :exc:`DecoratorStackingException` to be raised.

    Stacking of different types of decorators (ie. :func:`returns` and
    :func:`accepts`)
    is possible though and will neither raise an exception nor break anything.

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
.. autoexception:: ArgvalidateException

.. autoexception:: ArgumentTypeException
.. autoexception:: ReturnValueTypeException
.. autoexception:: DecoratorNonKeyLengthException
.. autoexception:: DecoratorKeyUnspecifiedException
.. autoexception:: DecoratorStackingException
