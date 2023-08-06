Supported options
=================

The recipe supports the following options:

.. Note to recipe author!
   ----------------------
   For each option the recipe uses you shoud include a description
   about the purpose of the option, the format and semantics of the
   values it accepts, whether it is mandatory or optional and what the
   default value is if it is omitted.

option
    Description for ``option``...
    Option is here to identify which option will be the concatenated

target
    Description for ``target``...
    Target is the target part that will receive the concatenated option from different parts

parts
    Description for ``parts``...
    Part is the list of different parts from which the option will be concatenated 


Example usage
=============

.. Note to recipe author!
   ----------------------
   zc.buildout provides a nice testing environment which makes it
   relatively easy to write doctests that both demonstrate the use of
   the recipe and test it.
   You can find examples of recipe doctests from the PyPI, e.g.
   
     http://pypi.python.org/pypi/zc.recipe.egg

   The PyPI page for zc.buildout contains documentation about the test
   environment.

     http://pypi.python.org/pypi/zc.buildout#testing-support

   Below is a skeleton doctest that you can start with when building
   your own tests.

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = test1
    ...
    ... [test1]
    ... recipe = my.macro.concat
    ... option = %(foo)s
    ... target = %(bar)s
    ... parts = test2
    ...         test3
    ... [test2]
    ... myconfig = be smart
    ... [test3]
    ... myconfig = dont worry
    ... [test4]
    ... myconfig =
    ... """ % { 'foo' : 'myconfig', 'bar' : 'test4'})

Running the buildout gives us::

    >>> print 'start', system(buildout) 
    start...
    Installing test1.
    <BLANKLINE>


