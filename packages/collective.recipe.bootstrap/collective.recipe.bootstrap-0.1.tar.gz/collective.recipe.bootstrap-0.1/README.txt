Introduction
============

This recipe satisfies the (perhaps) not-so-common use case of "I want to keep
my buildout bootstrap.py file up to date without having to manually download
it from svn.zope.org."

It also makes it possible to add a bootstrap.py file to a buildout created
via 'buildout init', for subsequent checking-in to the repo of your choice.

In other words, this recipe makes it possible to avoid typing:
% svn cat svn://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap/bootstrap.py > bootstrap.py

Just add a part and define this recipe. E.g.

[buildout]
parts += bootstrap

[bootstrap]
recipe = collective.recipe.bootstrap

and when you run buildout, this recipe will do the rest.

.. contents::

- Code repository: http://svn.plone.org/svn/collective/buildout/collective.recipe.bootstrap/
- Questions and comments to aclark@aclark.net
- Report bugs at aclark@aclark.net
