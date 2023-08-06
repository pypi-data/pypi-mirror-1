Introduction
============

This package is a bridge between `z3c.caching`_ and `CacheSetup`_: it takes
rulesets configured via z3c.caching and looks for a rule with the same id
in your current CacheSetup configuration. That rule is then used to set the
caching headers for the response.

This makes it possible to cache content which CacheSetup itself can
not handle (such as browser views).

Installation
============

To use ``five.caching`` you need only need to load its zcml.


Usage
=====

The only thing you need to do to enable five.caching to do its work is loads
its zcml.

A common problem you might notice is that CacheSetup rules often use
``python:object.modified()`` as expression, which does not work with
all objects supported by `z3c.caching` and `five.caching`. As an alternative
this package provides a ``lastmodified`` browser view which returns the same
information. You can use it by configuring ``object/@@lastmodified`` as
expression in your CacheSetup rules.


.. _z3c.caching: http://pypi.python.org/z3c.caching
.. _CacheSetup: http://plone.org/products/cachefu

