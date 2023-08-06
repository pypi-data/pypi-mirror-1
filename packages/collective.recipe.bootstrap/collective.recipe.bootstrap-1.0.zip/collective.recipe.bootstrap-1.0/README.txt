
.. contents::

- Code repository: http://svn.plone.org/svn/collective/buildout/collective.recipe.bootstrap/
- Questions and comments: aclark@aclark.net
- Report bugs: aclark@aclark.net

Introduction
============

This recipe satisfies the (perhaps not-so-common) use case of "I want to keep
my buildout bootstrap.py file up to date without having to manually download
it from svn.zope.org." It also makes it possible to add a bootstrap.py file 
to a buildout created via ``buildout init``. In other words, with this recipe 
you can avoid having to do::

    % svn cat svn://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap/bootstrap.py > bootstrap.py

Just add a new ``section``, then refer to it in your buildout section's
``parts``. E.g.::

    [buildout]
    parts =
        ...
        bootstrap

    [bootstrap]
    recipe = collective.recipe.bootstrap

Now whenever you run buildout, this recipe will update your bootstrap.py file.
