===================
iw.releaser package
===================

.. contents::

What is iw.releaser ?
=====================

iw.releaser is a setuptools extension that allows you to release an egg.

It performs the following steps:

- runs the tests over the egg, using zope.testing
- raises the version number in setup.py
- create a branch and a tag for the version
- upload if asked to the cheeshop 


How to use iw.releaser ?
========================

Go into your package root and run::

    $ python setup.py release

There is some command line options::

    $ python setup.py release -h
    ...
    Options for 'release' command:
      --testing (-t)  run tests before anything
      --release (-r)  release package
      --upload (-u)   upload package
      --version       new version number
      --auto (-a)     automatic mode
    ...

To make a release without any question, run this command with your new version
number::

    $ python setup.py release -a --version=0.2

