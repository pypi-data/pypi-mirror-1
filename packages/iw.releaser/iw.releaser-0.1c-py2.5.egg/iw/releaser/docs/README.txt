===================
iw.releaser package
===================

.. contents::

What is iw.releaser ?
=====================

iw.releaser is a setuptools extension that allows you to release an egg.

it performs the following steps:

- runs the tests over the egg, using zope.testing
- raises the version number in setup.py
- create a branch and a tag for the version
- upload if asked to the cheeshop 


How to use iw.releaser ?
========================

go into your package root and run:

$ python setup.py release

