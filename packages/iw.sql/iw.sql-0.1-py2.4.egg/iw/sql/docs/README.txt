==============
iw.sql package
==============

.. contents::

What is iw.sql ?
================

iw.sql provides a zope 3 utility on the top of z3c.sqlalchemy one, with
some extra features:

- when a SQL server is restarted, any session in memory will fail on next
  query. iw.sql prevents it by providing a session wrapper that knows
  how to relaunch it


How to use iw.sql ?
===================

Explain here how the package is used. Points to doctests here !




