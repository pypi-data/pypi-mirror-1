==========
eggchecker
==========

This is a small set of command extensions for `setuptools` that allows to run:

- QA tests on your package
- zope.testing 

`qa`: QA tests
==============

Runs as long as it has a `setup.py` on the root. It adds a new command
called `qa`. To run it, go into your package and type::

    $ python setup.py qa

At this time it simply runs `pyflakes` over the code.

`ztest`: zope.testing
=====================

Runs `zope.testing` over the package::

    $ python setup.py ztest


