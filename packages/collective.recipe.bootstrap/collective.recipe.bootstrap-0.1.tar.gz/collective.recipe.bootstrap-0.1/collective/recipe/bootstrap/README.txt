Supported options
=================

N/A


Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = test1
    ...
    ... [test1]
    ... recipe = collective.recipe.bootstrap
    ... """

Running the buildout gives us::

    >>> print 'start', system(buildout) 
    start...
    Installing test1.
    <BLANKLINE>
