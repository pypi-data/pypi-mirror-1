.. _argvalidate-envvars:

argvalidate environment variables
=================================

argvalidate lets you control its behaviour via two environment variables.

These variables are documented below.

.. envvar:: ARGVALIDATE_WARN

Defines whether argvalidate should raise exceptions on errors (value: `0`, 
default) or whether warnings should be generated (value: non-`0`).

.. note::

   The unit tests shipping with argvalidate turn off warnings so they can
   check if the respective exceptions have been raised.

.. envvar:: ARGVALIDATE_WARN_KWARG_AS_ARG

Defines whether argvalidate should generate a warning if a keyword argument
has been passed as a non-keyword argument (value: non-`0`) or not (value: `0`,
default).

