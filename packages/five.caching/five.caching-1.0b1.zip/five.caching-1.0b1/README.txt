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


.. _z3c.caching: http://pypi.python.org/z3c.caching
.. _CacheSetup: http://plone.org/products/cachefu

